import logging
import logging.handlers
import re
import time

from flask import g, session

from CTFd.utils.user import get_ip

# Sensitive keys to redact from logs
SENSITIVE_KEYS = {"password", "secret", "token", "nonce", "api_key", "flag"}


def redact_sensitive(data):
    """Recursively redacts sensitive keys from log properties"""
    if isinstance(data, dict):
        clean = {}
        for k, v in data.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                clean[k] = "[REDACTED]"
            else:
                clean[k] = redact_sensitive(v)
        return clean
    elif isinstance(data, str):
        # Redact potential authorization tokens or passwords in strings
        return re.sub(r"(?i)(bearer\s+|password=)[^\s&]+", r"\1[REDACTED]", data)
    return data


def log(logger_name, format_str=None, **kwargs):
    format_str = format_str or kwargs.pop("format", "")
    logger_inst = logging.getLogger(logger_name)
    request_id = getattr(g, "request_id", "N/A")
    props = {
        "id": session.get("id", "anonymous"),
        "date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "ip": get_ip(),
        "request_id": request_id,
    }
    clean_kwargs = redact_sensitive(kwargs)
    props.update(clean_kwargs)
    try:
        msg = f"[{request_id}] " + format_str.format(**props)
    except Exception:
        msg = f"[{request_id}] " + format_str + f" | data={clean_kwargs}"
    logger_inst.info(msg)
