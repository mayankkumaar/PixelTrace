from __future__ import annotations

import base64
import json

from app.core.security import sha256_hex, sign_payload, utc_now_iso


def build_payload(
    user_id: str,
    device_id: str,
    session_external_id: str,
    ip_address: str,
    segment_id: str,
) -> tuple[dict, str]:
    payload = {
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_external_id,
        "ip_hash": sha256_hex(ip_address),
        "timestamp": utc_now_iso(),
        "segment_id": segment_id,
        "version": "v1",
    }
    signature = sign_payload(payload)
    return payload, signature


def compact_payload(payload: dict, signature: str) -> str:
    blob = {"p": payload, "s": signature}
    raw = json.dumps(blob, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def expand_payload(compact: str) -> tuple[dict, str]:
    raw = base64.urlsafe_b64decode(compact.encode("utf-8")).decode("utf-8")
    blob = json.loads(raw)
    return blob["p"], blob["s"]
