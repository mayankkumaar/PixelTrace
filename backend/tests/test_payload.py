from app.core.security import verify_payload
from app.services.payload_service import build_payload, compact_payload, expand_payload


def test_payload_sign_and_verify_roundtrip():
    payload, signature = build_payload(
        user_id="u1",
        device_id="d1",
        session_external_id="s1",
        ip_address="1.2.3.4",
        segment_id="seg1",
    )
    assert verify_payload(payload, signature)

    compact = compact_payload(payload, signature)
    decoded_payload, decoded_signature = expand_payload(compact)

    assert decoded_payload == payload
    assert decoded_signature == signature
    assert verify_payload(decoded_payload, decoded_signature)
