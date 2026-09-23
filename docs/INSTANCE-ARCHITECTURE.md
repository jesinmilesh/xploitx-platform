# XploitX CTF Platform — Dynamic Challenge Instance Architecture

## 1. Threat Model & Isolation Objectives

Allowing participants to interact with running software (binary exploitation, web services, kernel challenges) introduces unique security risks:
1. **Host Compromise**: Malicious participants attempting container escape or host filesystem access.
2. **Denial of Service (DoS)**: Resource exhaustion (CPU/RAM bombs, fork bombs, disk fill attacks).
3. **Cross-Tenant Attack**: Participants attacking other participants' containers or internal CTFd databases.

---

## 2. Isolation Architecture

```
XploitX Web API (ctfd container)
       │
       │ HTTP API with HMAC Token Auth (Internal Network)
       ▼
Instance Manager Daemon (Port 9000)
       │
       │ Unix Domain Socket (/var/run/docker.sock)
       ▼
Isolated Container Runtime
  ├─ Network: "challenge-network" (Isolated bridge)
  ├─ cgroup CPU Quota: 0.5 CPU
  ├─ cgroup RAM Limit: 256MB
  ├─ cgroup PID Limit: 100
  ├─ Capabilities: CAP_DROP = ALL
  ├─ Security Opt: no-new-privileges:true
  └─ Port Range: 30000 - 35000 (Randomly allocated)
```

---

## 3. Strict Container Hardening Rules

Every challenge instance spawned by the Instance Manager enforces:
1. **Dropped Linux Capabilities**: `CapDrop = ["ALL"]` prevents containers from executing privileged syscalls or raw network packet crafting.
2. **No Privilege Escalation**: `no-new-privileges:true` prevents `setuid` binaries inside containers from escalating to root.
3. **PIDs Limit**: Capped at `100` to prevent fork bombs from exhausting host OS thread tables.
4. **Memory & CPU Limits**: Hard capped at `256MB` and `0.5 vCPU` per instance.
5. **Network Segregation**: Containers are placed on the isolated `challenge-network` bridge and cannot communicate with the `internal` network containing `db` and `cache`.
6. **Automatic Reaper**: A background daemon continuously polls instances; containers are automatically stopped and destroyed upon reaching expiration (default: 30 minutes).

---

## 4. API Endpoints

### 1. Launch Instance
```http
POST /api/v1/challenges/{challenge_id}/instances
Authorization: Bearer <session_cookie>
```
Response:
```json
{
  "success": true,
  "data": {
    "instance_id": "8f9a2b1c4e0d",
    "status": "RUNNING",
    "endpoint": "ctf.xploitx.org:30042",
    "port": 30042,
    "expires_at": "2026-09-23T12:30:00Z"
  }
}
```

### 2. Check Instance Status
```http
GET /api/v1/instances/{instance_id}
```
*Note: Protected by IDOR validation. Only the instance owner (user/team) or an admin can access this endpoint.*

### 3. Terminate Instance
```http
DELETE /api/v1/instances/{instance_id}
```
*Note: Protected by IDOR validation. Immediately releases the allocated port and destroys the container.*
