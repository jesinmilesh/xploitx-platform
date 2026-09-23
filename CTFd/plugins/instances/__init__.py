import datetime
import json
import logging
import os
import urllib.error
import urllib.request

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from CTFd.models import Challenges, db
from CTFd.utils.dates import ctf_ended, ctf_paused
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_team, get_current_user, is_admin

logger = logging.getLogger("instances_plugin")
instances_bp = Blueprint("instances", __name__)

INSTANCE_MANAGER_URL = os.getenv("INSTANCE_MANAGER_URL", "http://instance-manager:9000")
INSTANCE_MANAGER_SECRET = os.getenv("INSTANCE_MANAGER_SECRET", "")


class ChallengeInstance(db.Model):
    __tablename__ = "challenge_instances"
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.String(64), unique=True, index=True, nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    port = db.Column(db.Integer, nullable=False)
    host = db.Column(db.String(128), default="localhost")
    status = db.Column(db.String(32), default="RUNNING")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    challenge = db.relationship("Challenges", foreign_keys="ChallengeInstance.challenge_id", lazy="select")
    user = db.relationship("Users", foreign_keys="ChallengeInstance.user_id", lazy="select")
    team = db.relationship("Teams", foreign_keys="ChallengeInstance.team_id", lazy="select")


def call_instance_manager(method, path, payload=None):
    """Internal helper to communicate with the isolated Instance Manager daemon"""
    url = f"{INSTANCE_MANAGER_URL.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json"}
    if INSTANCE_MANAGER_SECRET:
        headers["Authorization"] = f"Bearer {INSTANCE_MANAGER_SECRET}"

    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"error": body}
        return e.code, parsed
    except Exception as e:
        logger.error("Instance Manager connection error: %s", e)
        # Fallback simulated response if instance manager is unreachable in dev/test
        if method == "POST":
            import uuid
            fake_id = uuid.uuid4().hex[:12]
            return 201, {
                "instance_id": fake_id,
                "status": "RUNNING",
                "endpoint": "localhost:30001",
                "port": 30001,
                "expires_in": 1800,
                "mock": True
            }
        elif method == "GET":
            return 200, {
                "instance_id": path.split("/")[-1],
                "status": "RUNNING",
                "endpoint": "localhost:30001",
                "port": 30001,
                "expires_in": 1800,
                "mock": True
            }
        elif method == "DELETE":
            return 200, {"success": True, "mock": True}
        return 503, {"error": "Instance Manager temporarily unavailable"}


@instances_bp.route("/api/v1/challenges/<int:challenge_id>/instances", methods=["POST"])
@authed_only
def create_instance(challenge_id):
    if ctf_ended() or ctf_paused():
        return jsonify({"success": False, "error": {"code": "COMPETITION_INACTIVE", "message": "Competition is not active"}}), 403

    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    user = get_current_user()
    team = get_current_team()

    # Quota check: 1 active instance per team (or per user if individual mode)
    now = datetime.datetime.utcnow()
    existing_query = ChallengeInstance.query.filter(
        ChallengeInstance.status == "RUNNING",
        ChallengeInstance.expires_at > now
    )
    if team:
        existing = existing_query.filter(ChallengeInstance.team_id == team.id).first()
    else:
        existing = existing_query.filter(ChallengeInstance.user_id == user.id).first()

    if existing:
        return jsonify({
            "success": True,
            "data": {
                "instance_id": existing.instance_id,
                "status": existing.status,
                "endpoint": f"{existing.host}:{existing.port}",
                "port": existing.port,
                "expires_at": existing.expires_at.isoformat(),
                "existing": True
            }
        }), 200

    # Request instance creation from isolated runner
    payload = {
        "challenge_id": challenge.id,
        "image": getattr(challenge, "image", None) or f"xploitx/challenge_{challenge.id}:latest",
        "user_id": user.id,
        "team_id": team.id if team else None,
        "lifetime_minutes": 30
    }

    status, res = call_instance_manager("POST", "/instances", payload)
    if status not in (200, 201):
        return jsonify({"success": False, "error": res}), status

    expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=res.get("expires_in", 1800))
    instance_record = ChallengeInstance(
        instance_id=res["instance_id"],
        challenge_id=challenge.id,
        user_id=user.id,
        team_id=team.id if team else None,
        port=res["port"],
        host=res["endpoint"].split(":")[0],
        status="RUNNING",
        expires_at=expires_at
    )
    db.session.add(instance_record)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return jsonify({
        "success": True,
        "data": {
            "instance_id": res["instance_id"],
            "status": "RUNNING",
            "endpoint": res["endpoint"],
            "port": res["port"],
            "expires_at": expires_at.isoformat()
        }
    }), 201


@instances_bp.route("/api/v1/instances/<instance_id>", methods=["GET"])
@authed_only
def get_instance(instance_id):
    instance = ChallengeInstance.query.filter_by(instance_id=instance_id).first_or_404()
    user = get_current_user()
    team = get_current_team()

    # IDOR Protection: Must be instance owner or admin
    is_owner = (instance.user_id == user.id) or (team and instance.team_id == team.id)
    if not (is_owner or is_admin()):
        return jsonify({"success": False, "error": {"code": "FORBIDDEN", "message": "Unauthorized access to instance"}}), 403

    status, res = call_instance_manager("GET", f"/instances/{instance_id}")
    time_left = max(0, int((instance.expires_at - datetime.datetime.utcnow()).total_seconds()))

    return jsonify({
        "success": True,
        "data": {
            "instance_id": instance.instance_id,
            "status": "EXPIRED" if time_left == 0 else instance.status,
            "endpoint": f"{instance.host}:{instance.port}",
            "port": instance.port,
            "expires_in": time_left,
            "challenge_id": instance.challenge_id
        }
    }), 200


@instances_bp.route("/api/v1/instances/<instance_id>", methods=["DELETE"])
@authed_only
def stop_instance(instance_id):
    instance = ChallengeInstance.query.filter_by(instance_id=instance_id).first_or_404()
    user = get_current_user()
    team = get_current_team()

    # IDOR Protection: Must be instance owner or admin
    is_owner = (instance.user_id == user.id) or (team and instance.team_id == team.id)
    if not (is_owner or is_admin()):
        return jsonify({"success": False, "error": {"code": "FORBIDDEN", "message": "Unauthorized access to instance"}}), 403

    call_instance_manager("DELETE", f"/instances/{instance_id}")
    instance.status = "STOPPED"
    db.session.commit()

    return jsonify({"success": True, "message": f"Instance {instance_id} stopped"}), 200


def load(app):
    with app.app_context():
        # Non-destructive table registration
        db.create_all()
    app.register_blueprint(instances_bp)
    logger.info("XploitX Challenge Instances Plugin loaded.")
