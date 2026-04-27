CREATE TABLE IF NOT EXISTS stream_sessions (
    id TEXT PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    subscriber_name VARCHAR(255) NOT NULL,
    device_id VARCHAR(128) NOT NULL,
    ip_hash VARCHAR(255) NOT NULL,
    segment_id VARCHAR(128) NOT NULL,
    session_external_id VARCHAR(128) UNIQUE NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS watermark_payloads (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES stream_sessions(id),
    payload_json JSONB NOT NULL,
    hmac_signature VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS detection_events (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES stream_sessions(id),
    source_clip_name VARCHAR(255) NOT NULL,
    decoded_payload JSONB NOT NULL,
    verification_status VARCHAR(64) NOT NULL,
    confidence_score FLOAT NOT NULL,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS forensic_reports (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES stream_sessions(id),
    detection_id TEXT NOT NULL REFERENCES detection_events(id),
    report_path VARCHAR(512) NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);
