"""
PixelTrace – Live Stream Piracy Detection
==========================================
Premium Streamlit frontend for AI-based forensic watermark detection.
Integrates with the FastAPI backend running at http://localhost:8000.
"""

import requests
import streamlit as st
from typing import cast
from streamlit.runtime.uploaded_file_manager import UploadedFile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api/v1"
DETECTION_ENDPOINT = f"{API_BASE}/portal/broadcaster/decode"
ENCODE_ENDPOINT = f"{API_BASE}/portal/viewer/encode"
REQUEST_TIMEOUT_SECONDS = 600  # video analysis can be slow on large files


# ---------------------------------------------------------------------------
# Custom CSS — injected once at app startup
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global ── */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background: #090b11;
}

/* Hide default Streamlit header chrome */
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Hero Section ── */
.hero-container {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(37, 99, 235, 0.12);
    border: 1px solid rgba(37, 99, 235, 0.25);
    color: #60a5fa;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    margin-bottom: 1.25rem;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin: 0 0 0.75rem;
    background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1.1rem;
    font-weight: 400;
    color: #64748b;
    max-width: 560px;
    margin: 0 auto;
    text-align: center;
    display: inline-block;
}
.hero-divider {
    width: 64px;
    height: 3px;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    border-radius: 999px;
    margin: 2rem auto 0;
}

/* ── Glass Card ── */
.glass-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}
.glass-card-header {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.glass-card-header .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.dot-blue  { background: #2563eb; }
.dot-green { background: #16a34a; }
.dot-red   { background: #dc2626; }

/* ── Upload Area ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02);
    border: 2px dashed rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.75rem;
    transition: border-color 0.3s ease, background 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(37, 99, 235, 0.4);
    background: rgba(37, 99, 235, 0.04);
}

/* ── File info pill ── */
.file-info {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(37, 99, 235, 0.1);
    border: 1px solid rgba(37, 99, 235, 0.2);
    color: #93c5fd;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    margin-top: 0.75rem;
}

/* ── Primary Button ── */
div.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.75rem 2rem !important;
    letter-spacing: 0.02em;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 24px rgba(37, 99, 235, 0.25) !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(37, 99, 235, 0.4) !important;
}
div.stButton > button:disabled {
    background: rgba(255,255,255,0.06) !important;
    color: #475569 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Result Cards ── */
.result-card {
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-top: 1rem;
}
.result-card-success {
    background: rgba(22, 163, 106, 0.08);
    border: 1px solid rgba(22, 163, 106, 0.2);
}
.result-card-error {
    background: rgba(220, 38, 38, 0.08);
    border: 1px solid rgba(220, 38, 38, 0.2);
}
.result-card-warning {
    background: rgba(234, 179, 8, 0.08);
    border: 1px solid rgba(234, 179, 8, 0.2);
}
.result-title {
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: 1.25rem;
}
.result-title-success { color: #4ade80; }
.result-title-error   { color: #f87171; }
.result-title-warning { color: #facc15; }

/* ── Metric Tiles ── */
.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
.metric-tile {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 0.35rem;
}
.metric-value {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
    word-break: break-all;
}

/* ── Confidence Bar ── */
.confidence-bar-track {
    width: 100%;
    height: 8px;
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    margin-top: 0.6rem;
    overflow: hidden;
}
.confidence-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s ease;
}

/* ── Report Button ── */
.report-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(37, 99, 235, 0.12);
    border: 1px solid rgba(37, 99, 235, 0.25);
    color: #60a5fa;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.65rem 1.5rem;
    border-radius: 10px;
    text-decoration: none;
    margin-top: 1.25rem;
    transition: all 0.2s ease;
}
.report-btn:hover {
    background: rgba(37, 99, 235, 0.2);
    border-color: rgba(37, 99, 235, 0.45);
    color: #93c5fd;
}

/* ── Timeline (How It Works) ── */
.timeline {
    position: relative;
    padding-left: 2.5rem;
}
.timeline::before {
    content: '';
    position: absolute;
    left: 0.85rem;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(180deg, #2563eb 0%, #7c3aed 50%, #ec4899 100%);
    border-radius: 999px;
}
.timeline-item {
    position: relative;
    padding-bottom: 2rem;
}
.timeline-item:last-child { padding-bottom: 0; }
.timeline-dot {
    position: absolute;
    left: -1.75rem;
    top: 0.2rem;
    width: 14px; height: 14px;
    background: #2563eb;
    border: 3px solid #090b11;
    border-radius: 50%;
    z-index: 1;
}
.timeline-step-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.3rem;
}
.timeline-step-desc {
    font-size: 0.9rem;
    color: #94a3b8;
    line-height: 1.6;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.6rem 1.5rem;
    color: #64748b;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(37, 99, 235, 0.15) !important;
    color: #60a5fa !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #334155;
    font-size: 0.78rem;
    padding: 2rem 0 1rem;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin-top: 3rem;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #2563eb !important;
}

/* ── Hide Streamlit default elements ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-weight: 600;
    font-size: 0.9rem;
    color: #94a3b8;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0.6rem 0.75rem !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
}
</style>
"""


# ---------------------------------------------------------------------------
# API Integration
# ---------------------------------------------------------------------------

def call_detection_api(file: UploadedFile) -> dict:
    """
    Send the uploaded video to the broadcaster/decode endpoint.

    This endpoint auto-scans against all existing viewer sessions
    and returns the best match (no session_external_id needed).

    Returns dict with:
        ok    – True if the HTTP request succeeded (2xx).
        json  – Parsed JSON body (None on network errors).
        error – Human-readable error message (empty on success).
    """
    try:
        # The broadcaster/decode endpoint expects field name "encoded_video"
        response = requests.post(
            DETECTION_ENDPOINT,
            files={"encoded_video": (file.name, file.getvalue(), file.type or "video/mp4")},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        try:
            body = response.json()
        except ValueError:
            body = None

        if response.ok:
            return {"ok": True, "json": body, "error": ""}
        else:
            msg = ""
            if body and isinstance(body, dict):
                msg = body.get("message", body.get("detail", ""))
            return {
                "ok": False,
                "json": body,
                "error": msg or f"Server returned HTTP {response.status_code}",
            }

    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "json": None,
            "error": (
                "Cannot connect to the backend. "
                f"Is it running at {BACKEND_URL}?"
            ),
        }
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "json": None,
            "error": (
                "Request timed out. The video may be too large "
                "or the server is under heavy load."
            ),
        }
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "json": None, "error": f"Unexpected error: {exc}"}


def call_encode_api(
    *,
    viewer_login_id: str,
    subscriber_name: str,
    device_id: str,
    ip_address: str,
    segment_id: str,
    source_video: UploadedFile,
) -> dict:
    """
    Send the viewer encode request and return status + payload.

    Returns dict with:
        ok    – True if the HTTP request succeeded (2xx).
        json  – Parsed JSON body (None on network errors).
        error – Human-readable error message (empty on success).
    """
    data = {
        "viewer_login_id": viewer_login_id,
        "subscriber_name": subscriber_name,
        "device_id": device_id,
        "ip_address": ip_address,
        "segment_id": segment_id,
        "use_project_raw_video": "false",
        "project_raw_video_name": "pirated_match.mp4",
    }
    files = {
        "source_video": (
            source_video.name,
            source_video.getvalue(),
            source_video.type or "video/mp4",
        )
    }

    try:
        response = requests.post(
            ENCODE_ENDPOINT,
            data=data,
            files=files,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        try:
            body = response.json()
        except ValueError:
            body = None

        if response.ok:
            return {"ok": True, "json": body, "error": ""}
        msg = ""
        if body and isinstance(body, dict):
            msg = body.get("message", body.get("detail", ""))
        return {
            "ok": False,
            "json": body,
            "error": msg or f"Server returned HTTP {response.status_code}",
        }
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "json": None,
            "error": (
                "Cannot connect to the backend. "
                f"Is it running at {BACKEND_URL}?"
            ),
        }
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "json": None,
            "error": (
                "Request timed out. The video may be too large "
                "or the server is under heavy load."
            ),
        }
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "json": None, "error": f"Unexpected error: {exc}"}


# ---------------------------------------------------------------------------
# UI Renderers
# ---------------------------------------------------------------------------

def render_header() -> None:
    """Render the centered hero header with brand, title, and subtitle."""
    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title">🎬 PixelTrace</h1>
            <p class="hero-subtitle">AI-powered forensic watermarking for piracy detection</p>
             <div class="hero-divider"></div>
         </div>
         """,
        unsafe_allow_html=True,
    )


def render_upload() -> UploadedFile | None:
    """
    Render the upload card and return the uploaded file (or None).
    """
    st.markdown(
        '<div class="glass-card">'
        '<div class="glass-card-header">'
        '<span class="dot dot-blue"></span>Upload Clip'
        "</div>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload a suspected pirated clip to identify its source",
        type=["mp4", "avi", "mov"],
        label_visibility="visible",
    )

    # Show file metadata pill when a file is selected
    if uploaded_file is not None:
        size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.markdown(
            f'<div class="file-info">'
            f"📎 {uploaded_file.name} &nbsp;·&nbsp; {size_mb:.1f} MB"
            f"</div>",
            unsafe_allow_html=True,
        )

        with st.expander("Preview uploaded clip"):
            st.video(uploaded_file)

    st.markdown("</div>", unsafe_allow_html=True)

    return uploaded_file


def _confidence_color(conf: float) -> str:
    """Return a CSS color string based on confidence level."""
    if conf >= 0.8:
        return "#22c55e"
    if conf >= 0.5:
        return "#eab308"
    return "#ef4444"


def render_results(response_json: dict | None, is_error: bool = False) -> None:
    """
    Display detection results inside a styled card.

    The actual backend returns a DetectionResponse with flat fields:
        subscriber_name, user_id, device_id, ip_hash,
        leak_timestamp, session_external_id,
        verification_status, confidence_score,
        decoded_payload, report_path

    On error it returns: {"detail": "..."}
    """
    if response_json is None:
        st.markdown(
            '<div class="result-card result-card-warning">'
            '<div class="result-title result-title-warning">'
            "⚠ Empty Response</div>"
            "<p style='color:#94a3b8;margin:0;'>"
            "The backend returned an empty response.</p></div>",
            unsafe_allow_html=True,
        )
        return

    # ── Error from backend (4xx / 5xx with detail) ───────────────────────
    if is_error:
        detail = response_json.get("detail", "Unknown error")
        st.markdown(
            f"""
            <div class="result-card result-card-error">
                <div class="result-title result-title-error">
                    ❌&ensp;Detection Failed
                </div>
                <p style="color:#94a3b8; margin:0; font-size:0.9rem;">
                    {detail}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Successful detection ─────────────────────────────────────────────
    user_id = response_json.get("user_id", "N/A")
    subscriber_name = response_json.get("subscriber_name", "N/A")
    session_id = response_json.get("session_external_id", "N/A")
    device_id = response_json.get("device_id", "N/A")
    timestamp = response_json.get("leak_timestamp", "N/A")
    verification = response_json.get("verification_status", "unknown")
    confidence = response_json.get("confidence_score")
    report_path = response_json.get("report_path")

    # Parse confidence safely
    try:
        conf_float = float(confidence) if confidence is not None else 0.0
    except (TypeError, ValueError):
        conf_float = 0.0
    conf_pct = f"{conf_float * 100:.0f}%" if confidence is not None else "N/A"
    conf_color = _confidence_color(conf_float)
    conf_width = f"{min(conf_float * 100, 100):.0f}"

    # Verification badge — maps to backend confidence tiers
    if verification == "verified_high":
        badge = '<span style="color:#22c55e;font-weight:600;">✅ Verified (High Confidence)</span>'
    elif verification == "verified_medium":
        badge = '<span style="color:#60a5fa;font-weight:600;">✅ Verified (Medium Confidence)</span>'
    elif verification == "verified_low":
        badge = '<span style="color:#eab308;font-weight:600;">⚠ Verified (Low Confidence)</span>'
    elif verification == "unverified":
        badge = '<span style="color:#ef4444;font-weight:600;">❌ No Match</span>'
    else:
        badge = f'<span style="color:#94a3b8;font-weight:600;">{verification}</span>'

    html = f"""
    <div class="result-card result-card-success">
        <div class="result-title result-title-success">
            ✅&ensp;Leak Source Identified
        </div>
        <div style="margin-bottom:1rem;font-size:0.85rem;">Status: {badge}</div>
        <div class="metric-grid">
            <div class="metric-tile">
                <div class="metric-label">👤 User ID</div>
                <div class="metric-value">{user_id}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">🔑 Session ID</div>
                <div class="metric-value">{session_id}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">👤 Subscriber</div>
                <div class="metric-value">{subscriber_name}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">📱 Device ID</div>
                <div class="metric-value">{device_id}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">⏱ Leak Timestamp</div>
                <div class="metric-value">{timestamp}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">📊 Confidence</div>
                <div class="metric-value" style="color:{conf_color}">
                    {conf_pct}
                </div>
                <div class="confidence-bar-track">
                    <div class="confidence-bar-fill"
                         style="width:{conf_width}%;
                                background:{conf_color};"></div>
                </div>
            </div>
        </div>
    """

    # Report download link (report_path is a local file path on server;
    # we don't have a direct download URL, so show the path info)
    if report_path:
        html += (
            f'<div style="margin-top:1.25rem; padding:0.75rem 1rem; '
            f'background:rgba(37,99,235,0.08); border:1px solid rgba(37,99,235,0.2); '
            f'border-radius:10px; color:#93c5fd; font-size:0.85rem;">'
            f'📄 Forensic report generated at: <code style="color:#e2e8f0;">{report_path}</code>'
            f'</div>'
        )

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # Show raw decoded payload in expander
    decoded = response_json.get("decoded_payload")
    if decoded:
        with st.expander("Decoded Watermark Payload"):
            st.json(decoded)


def render_how_it_works() -> None:
    """Render the pipeline explainer as a styled vertical timeline."""
    st.markdown(
        """
        <div class="glass-card" style="margin-top:0.5rem;">
            <div class="glass-card-header">
                <span class="dot dot-blue"></span>How PixelTrace Works
            </div>
            <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:2rem;">
                PixelTrace unifies viewer watermarking and broadcaster
                verification in a single, secure workflow.
            </p>
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-step-title">
                        Step 1 — Encode a Unique Watermark
                    </div>
                    <div class="timeline-step-desc">
                        A viewer uploads a video and receives a
                        uniquely watermarked copy tied to their session.
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-dot" style="background:#7c3aed;"></div>
                    <div class="timeline-step-title">
                        Step 2 — Upload a Suspected Clip
                    </div>
                    <div class="timeline-step-desc">
                        Broadcasters submit a leaked or pirated clip
                        for forensic inspection.
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-dot" style="background:#a855f7;"></div>
                    <div class="timeline-step-title">
                        Step 3 — Multi-frame Decoding
                    </div>
                    <div class="timeline-step-desc">
                        PixelTrace analyzes multiple frames to recover
                        the embedded payload with resilience to edits.
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-dot" style="background:#ec4899;"></div>
                    <div class="timeline-step-title">
                        Step 4 — Source Identified (or Rejected)
                    </div>
                    <div class="timeline-step-desc">
                        The decoded watermark is matched against
                        session records to confirm the source or
                        report a clean no-match result.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render a minimal footer."""
    st.markdown(
        '<div class="footer">'
        "PixelTrace &copy; 2026 &mdash; AI-powered forensic watermark "
        "detection. All rights reserved."
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry-point: configure the page and orchestrate the UI."""

    # Page config — must be the first Streamlit command
    st.set_page_config(
        page_title="PixelTrace – AI-powered forensic watermarking",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Inject custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    if "encoded_video_bytes" not in st.session_state:
        st.session_state["encoded_video_bytes"] = None
    if "encoded_video_name" not in st.session_state:
        st.session_state["encoded_video_name"] = None
    if "latest_encode_response" not in st.session_state:
        st.session_state["latest_encode_response"] = None
    if "encode_error" not in st.session_state:
        st.session_state["encode_error"] = None

    # Hero header
    render_header()

    # Tabs
    viewer_tab, detection_tab, how_tab = st.tabs(
        ["  Viewer  ", "  Detection  ", "  How It Works  "]
    )

    # ── Viewer Tab ──────────────────────────────────────────────────────
    with viewer_tab:
        _pad_l, content, _pad_r = st.columns([1, 4, 1])
        with content:
            left_col, right_col = st.columns(2, gap="large")

            with left_col:
                st.markdown(
                    '<div class="glass-card">'
                    '<div class="glass-card-header">'
                    '<span class="dot dot-green"></span>Viewer Input'
                    "</div>",
                    unsafe_allow_html=True,
                )

                with st.form("viewer_encode_form", clear_on_submit=False):
                    viewer_login_id = st.text_input("Viewer Login ID", "viewer_1001")
                    subscriber_name = st.text_input("Subscriber Name", "Viewer 1001")
                    device_id = st.text_input("Device ID", "web_device_A1")
                    ip_address = st.text_input("IP Address", "10.21.34.56")
                    segment_id = st.text_input("Segment ID", "seg_01")
                    source_video = st.file_uploader(
                        "Upload Video for Encoding",
                        type=["mp4", "mov", "avi", "mkv"],
                        key="viewer_source",
                    )
                    if source_video is not None:
                        source_video = cast(UploadedFile, source_video)

                    encode_clicked = st.form_submit_button(
                        "🎬  Encode Video",
                        use_container_width=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)

                if encode_clicked:
                    st.session_state["encode_error"] = None

                    if source_video is None:
                        st.session_state["encode_error"] = (
                            "Please upload a video to encode before continuing."
                        )
                    else:
                        with st.spinner("Encoding watermark…"):
                            result = call_encode_api(
                                viewer_login_id=viewer_login_id,
                                subscriber_name=subscriber_name,
                                device_id=device_id,
                                ip_address=ip_address,
                                segment_id=segment_id,
                                source_video=source_video,
                            )

                        if not result["ok"]:
                            st.session_state["encode_error"] = result["error"]
                        else:
                            st.session_state["latest_encode_response"] = result["json"]

                            download_url = result["json"].get(
                                "encoded_video_download_url", ""
                            )
                            if download_url.startswith("http://") or download_url.startswith(
                                "https://"
                            ):
                                full_download_url = download_url
                            else:
                                full_download_url = f"{BACKEND_URL}{download_url}"

                            download_response = requests.get(
                                full_download_url, timeout=REQUEST_TIMEOUT_SECONDS
                            )
                            if not download_response.ok:
                                st.session_state["encode_error"] = (
                                    "Encoded video created, but download failed. "
                                    f"({download_response.status_code})"
                                )
                            else:
                                st.session_state["encoded_video_bytes"] = (
                                    download_response.content
                                )
                                st.session_state["encoded_video_name"] = result["json"].get(
                                    "encoded_video_name"
                                )

            with right_col:
                st.markdown(
                    '<div class="glass-card">'
                    '<div class="glass-card-header">'
                    '<span class="dot dot-blue"></span>Encoding Result'
                    "</div>",
                    unsafe_allow_html=True,
                )

                if st.session_state.get("encode_error"):
                    st.markdown(
                        f"""
                        <div class="result-card result-card-warning">
                            <div class="result-title result-title-warning">
                                ⚠&ensp;Encoding Issue
                            </div>
                            <p style="color:#94a3b8; margin:0; font-size:0.9rem;">
                                {st.session_state["encode_error"]}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif st.session_state.get("latest_encode_response"):
                    st.markdown(
                        """
                        <div class="result-card result-card-success">
                            <div class="result-title result-title-success">
                                ✅&ensp;Encoding Complete
                            </div>
                            <p style="color:#94a3b8; margin:0; font-size:0.9rem;">
                                The video has been watermarked successfully.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<p style='color:#64748b; margin:0;'>"
                        "Encode a video to see results here.</p>",
                        unsafe_allow_html=True,
                    )

                if st.session_state.get("latest_encode_response"):
                    st.markdown(
                        "<div style='height:1rem'></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        '<div class="glass-card" style="padding:1.5rem;">'
                        '<div class="glass-card-header">'
                        '<span class="dot dot-green"></span>Encoding Metadata'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    st.json(st.session_state["latest_encode_response"], expanded=False)
                    st.markdown("</div>", unsafe_allow_html=True)

                if st.session_state.get("encoded_video_bytes"):
                    st.markdown(
                        "<div style='height:1rem'></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        '<div class="glass-card" style="padding:1.5rem;">'
                        '<div class="glass-card-header">'
                        '<span class="dot dot-blue"></span>Encoded Video Download'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        "<p style='color:#94a3b8; margin:0 0 0.75rem;'>"
                        "Download the personalized watermarked video.</p>",
                        unsafe_allow_html=True,
                    )
                    st.download_button(
                        label="⬇️  Download Encoded Video",
                        data=st.session_state["encoded_video_bytes"],
                        file_name=st.session_state.get("encoded_video_name")
                        or "encoded_video.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                if st.session_state.get("encoded_video_bytes"):
                    st.markdown(
                        "<div style='height:1rem'></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        '<div class="glass-card" style="padding:1.5rem;">'
                        '<div class="glass-card-header">'
                        '<span class="dot dot-blue"></span>Encoded Video Preview'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    st.video(st.session_state["encoded_video_bytes"])
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

    # ── Detection Tab ────────────────────────────────────────────────────
    with detection_tab:
        # Center content using columns for visual balance
        _pad_l, content, _pad_r = st.columns([1, 3, 1])

        with content:
            uploaded_file = render_upload()
            if uploaded_file is not None:
                uploaded_file = cast(UploadedFile, uploaded_file)

            # Spacer
            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

            # Detect button — disabled when no file is uploaded
            detect_clicked = st.button(
                "🔍  Detect Source",
                disabled=(uploaded_file is None),
                use_container_width=True,
            )

            if detect_clicked and uploaded_file is not None:
                st.markdown(
                    "<div style='height:0.5rem'></div>", unsafe_allow_html=True
                )

                with st.spinner("Analyzing watermark…"):
                    result = call_detection_api(uploaded_file)

                if result["ok"]:
                    render_results(result["json"])
                elif result["json"] is not None:
                    # Server returned an error with a JSON body
                    render_results(result["json"], is_error=True)
                else:
                    # Network-level failure
                    st.markdown(
                        f"""
                        <div class="result-card result-card-warning">
                            <div class="result-title result-title-warning">
                                ⚠&ensp;Connection Error
                            </div>
                            <p style="color:#94a3b8; margin:0;
                                      font-size:0.9rem;">
                                {result['error']}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # ── How It Works Tab ─────────────────────────────────────────────────
    with how_tab:
        _pad_l2, content2, _pad_r2 = st.columns([1, 3, 1])
        with content2:
            render_how_it_works()

    # Footer
    render_footer()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
