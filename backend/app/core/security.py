from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone

from app.core.config import settings


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sign_payload(payload: dict) -> str:
    message = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        key=settings.payload_hmac_key.encode("utf-8"),
        msg=message,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return signature


def verify_payload(payload: dict, signature: str) -> bool:
    expected = sign_payload(payload)
    return hmac.compare_digest(expected, signature)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
