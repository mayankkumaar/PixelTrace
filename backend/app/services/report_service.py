from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_forensic_report(output_path: str, data: dict) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Forensic Attribution Report")
    y -= 30

    c.setFont("Helvetica", 10)
    fields = [
        ("Subscriber Name", data.get("subscriber_name")),
        ("User ID", data.get("user_id")),
        ("Device Information", data.get("device_id")),
        ("IP Address Hash", data.get("ip_hash")),
        ("Leak Timestamp", data.get("leak_timestamp")),
        ("Session ID", data.get("session_external_id")),
        ("Verification Status", data.get("verification_status")),
        ("Evidence Confidence Score", data.get("confidence_score")),
    ]

    for key, value in fields:
        c.drawString(40, y, f"{key}: {value}")
        y -= 18

    c.drawString(40, y - 8, "Decoded Payload:")
    y -= 24

    payload_lines = str(data.get("decoded_payload", {}))
    for chunk_start in range(0, len(payload_lines), 95):
        c.drawString(40, y, payload_lines[chunk_start : chunk_start + 95])
        y -= 15

    c.save()
    return output_path
