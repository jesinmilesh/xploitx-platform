#!/usr/bin/env python
"""
XploitX Isolated Challenge Instance Manager Daemon
Runs as an isolated service with access to the Docker daemon.
Executes challenge containers with strict cgroup limits, dropped capabilities,
isolated networking, and automatic lifecycle management.
"""
import http.server
import json
import logging
import os
import re
import socket
import sys
import threading
import time
import uuid
import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [InstanceManager] %(message)s"
)
logger = logging.getLogger("instance_manager")

SECRET_TOKEN = os.getenv("INSTANCE_MANAGER_SECRET", "")
PORT_RANGE_START = int(os.getenv("PORT_RANGE_START", 30000))
PORT_RANGE_END = int(os.getenv("PORT_RANGE_END", 35000))
MAX_LIFETIME_MINUTES = int(os.getenv("CONTAINER_MAX_LIFETIME_MINUTES", 30))
DEFAULT_MEM_LIMIT = os.getenv("CONTAINER_MEM_LIMIT", "256m")
DEFAULT_CPU_LIMIT = float(os.getenv("CONTAINER_CPU_LIMIT", "0.5"))
DEFAULT_PIDS_LIMIT = int(os.getenv("CONTAINER_PIDS_LIMIT", 100))
PUBLIC_HOST = os.getenv("INSTANCE_PUBLIC_HOST", "localhost")

# Thread-safe in-memory state tracking active instances and allocated ports
state_lock = threading.Lock()
active_instances = {}  # instance_id -> {container_id, port, expires_at, user_id, team_id, challenge_id}
allocated_ports = set()


def allocate_port():
    with state_lock:
        for p in range(PORT_RANGE_START, PORT_RANGE_END):
            if p not in allocated_ports:
                # Double check with OS socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(("127.0.0.1", p)) != 0:
                        allocated_ports.add(p)
                        return p
        raise RuntimeError("No ports available in configured range")


def release_port(port):
    with state_lock:
        allocated_ports.discard(port)


class DockerSocketClient:
    """Lightweight Docker Engine API client via /var/run/docker.sock"""
    def __init__(self, sock_path="/var/run/docker.sock"):
        self.sock_path = sock_path
        self.available = os.path.exists(sock_path)
        if not self.available:
            logger.warning("Docker socket %s not found. Running in simulation/mock mode.", sock_path)

    def _request(self, method, path, data=None):
        if not self.available:
            return 200, {"mock": True}

        class UnixHTTPConnection(http.client.HTTPConnection):
            def __init__(self, sock_path):
                super().__init__("localhost")
                self.sock_path = sock_path

            def connect(self):
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(self.sock_path)

        import http.client
        conn = UnixHTTPConnection(self.sock_path)
        body = json.dumps(data) if data else None
        headers = {"Content-Type": "application/json"} if body else {}
        try:
            conn.request(method, path, body=body, headers=headers)
            res = conn.getresponse()
            res_body = res.read().decode("utf-8")
            conn.close()
            try:
                parsed = json.loads(res_body) if res_body else {}
            except Exception:
                parsed = {"raw": res_body}
            return res.status, parsed
        except Exception as e:
            logger.error("Docker API error: %s", e)
            return 500, {"error": str(e)}

    def create_and_start(self, image, instance_id, host_port, internal_port=80, mem_limit="256m", cpu_quota=50000):
        if not self.available:
            return "mock-container-" + instance_id

        # 1. Create container
        create_payload = {
            "Image": image,
            "Labels": {
                "xploitx.instance_id": instance_id,
                "xploitx.managed": "true"
            },
            "HostConfig": {
                "PortBindings": {
                    f"{internal_port}/tcp": [{"HostPort": str(host_port)}]
                },
                "Memory": 256 * 1024 * 1024,
                "CpuQuota": int(cpu_quota),
                "PidsLimit": DEFAULT_PIDS_LIMIT,
                "CapDrop": ["ALL"],
                "SecurityOpt": ["no-new-privileges:true"],
                "NetworkMode": "challenge-network"
            }
        }
        status, res = self._request("POST", f"/containers/create?name=ctf_{instance_id}", create_payload)
        if status not in (200, 201):
            raise RuntimeError(f"Failed to create container: {res}")

        container_id = res.get("Id")
        # 2. Start container
        status, res = self._request("POST", f"/containers/{container_id}/start")
        if status not in (200, 204):
            raise RuntimeError(f"Failed to start container: {res}")

        return container_id

    def stop_and_remove(self, container_id):
        if not self.available or container_id.startswith("mock-"):
            return
        self._request("POST", f"/containers/{container_id}/stop?t=5")
        self._request("DELETE", f"/containers/{container_id}?force=true")


docker_client = DockerSocketClient()


def reaper_worker():
    """Background thread to reap expired challenge instances"""
    while True:
        try:
            now = time.time()
            to_remove = []
            with state_lock:
                for inst_id, info in list(active_instances.items()):
                    if now >= info["expires_at"]:
                        to_remove.append((inst_id, info["container_id"], info["port"]))

            for inst_id, c_id, port in to_remove:
                logger.info("Instance %s expired. Reaping container %s", inst_id, c_id)
                try:
                    docker_client.stop_and_remove(c_id)
                except Exception as e:
                    logger.error("Error stopping container: %s", e)
                release_port(port)
                with state_lock:
                    active_instances.pop(inst_id, None)

        except Exception as e:
            logger.error("Error in reaper loop: %s", e)
        time.sleep(15)


class InstanceRequestHandler(http.server.BaseHTTPRequestHandler):
    def _authenticate(self):
        auth_header = self.headers.get("Authorization", "")
        if SECRET_TOKEN and auth_header != f"Bearer {SECRET_TOKEN}":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
            return False
        return True

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if not self._authenticate():
            return

        if self.path == "/health":
            self._send_json(200, {"status": "ok", "active_instances": len(active_instances)})
            return

        match = re.match(r"^/instances/([a-zA-Z0-9_\-]+)$", self.path)
        if match:
            inst_id = match.group(1)
            with state_lock:
                info = active_instances.get(inst_id)
            if not info:
                self._send_json(404, {"error": "Instance not found"})
                return

            time_left = max(0, int(info["expires_at"] - time.time()))
            self._send_json(200, {
                "instance_id": inst_id,
                "status": "RUNNING" if time_left > 0 else "EXPIRED",
                "endpoint": f"{PUBLIC_HOST}:{info['port']}",
                "port": info["port"],
                "expires_in": time_left,
                "challenge_id": info["challenge_id"]
            })
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        if not self._authenticate():
            return

        if self.path == "/instances":
            content_length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))

            challenge_id = payload.get("challenge_id")
            image = payload.get("image", "alpine:latest")
            user_id = payload.get("user_id")
            team_id = payload.get("team_id")
            lifetime = min(payload.get("lifetime_minutes", MAX_LIFETIME_MINUTES), 120)

            # Prevent image injection: allow only sanitized alphanumeric repository/tag
            if not re.match(r"^[a-zA-Z0-9_\.\-\/]+(:[a-zA-Z0-9_\.\-]+)?$", image):
                self._send_json(400, {"error": "Invalid Docker image name"})
                return

            instance_id = uuid.uuid4().hex[:12]
            try:
                port = allocate_port()
                container_id = docker_client.create_and_start(
                    image=image,
                    instance_id=instance_id,
                    host_port=port,
                    internal_port=payload.get("internal_port", 80),
                    cpu_quota=int(DEFAULT_CPU_LIMIT * 100000)
                )
            except Exception as e:
                logger.error("Failed to provision instance: %s", e)
                self._send_json(500, {"error": f"Failed to provision container: {str(e)}"})
                return

            expires_at = time.time() + (lifetime * 60)
            with state_lock:
                active_instances[instance_id] = {
                    "container_id": container_id,
                    "port": port,
                    "expires_at": expires_at,
                    "user_id": user_id,
                    "team_id": team_id,
                    "challenge_id": challenge_id
                }

            logger.info("Created instance %s on port %s for user %s / team %s", instance_id, port, user_id, team_id)
            self._send_json(201, {
                "instance_id": instance_id,
                "status": "RUNNING",
                "endpoint": f"{PUBLIC_HOST}:{port}",
                "port": port,
                "expires_in": lifetime * 60
            })
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_DELETE(self):
        if not self._authenticate():
            return

        match = re.match(r"^/instances/([a-zA-Z0-9_\-]+)$", self.path)
        if match:
            inst_id = match.group(1)
            with state_lock:
                info = active_instances.pop(inst_id, None)

            if not info:
                self._send_json(404, {"error": "Instance not found"})
                return

            try:
                docker_client.stop_and_remove(info["container_id"])
            except Exception as e:
                logger.error("Error stopping container %s: %s", info["container_id"], e)
            release_port(info["port"])
            logger.info("Terminated instance %s and freed port %s", inst_id, info["port"])
            self._send_json(200, {"success": True, "message": f"Instance {inst_id} terminated"})
            return

        self._send_json(404, {"error": "Endpoint not found"})


def run_server():
    reaper = threading.Thread(target=reaper_worker, daemon=True)
    reaper.start()

    server = http.server.HTTPServer(("0.0.0.0", 9000), InstanceRequestHandler)
    logger.info("Instance Manager listening on port 9000...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Instance Manager...")
        server.server_close()


if __name__ == "__main__":
    run_server()
