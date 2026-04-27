# UI/UX Prototype Notes

## Investigator Dashboard Screens

1. Session Registration Panel
- Inputs: subscriber name, user ID, device ID, session ID, IP, segment ID
- Action: create session and payload

2. Payload Inspection Panel
- Input: session ID
- Output: payload JSON + HMAC signature

3. Piracy Detection Panel
- Input: session ID + pirated clip upload
- Action: run detection
- Output: decoded payload, verification status, confidence score, report path

## UX Principles

- Single-page workflow for faster investigations.
- Progressive disclosure: create session -> inspect payload -> detect clip.
- Confidence status color coding (green verified, yellow uncertain, red failed).
- Export-ready forensic report in one click.
