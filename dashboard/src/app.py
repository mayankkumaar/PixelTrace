from pathlib import Path

import requests
import streamlit as st

API_BASE = st.sidebar.text_input("API Base URL", "http://localhost:8000/api/v1")
API_ROOT = API_BASE.split("/api/v1")[0] if "/api/v1" in API_BASE else API_BASE.rstrip("/")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_SAMPLES_UPLOADS = PROJECT_ROOT / "backend" / "samples" / "uploads"

st.title("Personalized Stream Watermark Portal")
st.caption("Viewer-side personalized encoding and broadcaster-side forensic decoding")

if "encoded_video_bytes" not in st.session_state:
    st.session_state["encoded_video_bytes"] = None
if "encoded_video_name" not in st.session_state:
    st.session_state["encoded_video_name"] = None
if "latest_encode_response" not in st.session_state:
    st.session_state["latest_encode_response"] = None

viewer_tab, broadcaster_tab = st.tabs(["Viewer", "Broadcaster"])

with viewer_tab:
    st.subheader("Viewer Login and Watch")
    viewer_login_id = st.text_input("Viewer Login ID", "viewer_1001")
    subscriber_name = st.text_input("Subscriber Name", "Viewer 1001")
    device_id = st.text_input("Device ID", "web_device_A1")
    ip_address = st.text_input("IP Address", "10.21.34.56")
    segment_id = st.text_input("Segment ID", "seg_01")
    use_project_raw_video = st.checkbox("Use project raw video (single source for all users)", value=True)
    project_raw_video_name = st.text_input("Project Raw Video File Name", "pirated_match.mp4")

    source_video = None
    if use_project_raw_video:
        project_raw_path = BACKEND_SAMPLES_UPLOADS / project_raw_video_name
        if project_raw_path.exists():
            st.caption(f"Using project video: {project_raw_path}")
            st.video(project_raw_path.read_bytes())
        else:
            st.warning(f"Project video not found: {project_raw_path}")
    else:
        source_video = st.file_uploader(
            "Upload Original Video to Watch",
            type=["mp4", "mov", "avi", "mkv"],
            key="viewer_source",
        )
        if source_video is not None:
            st.caption("Original video preview")
            st.video(source_video)

    if st.button("Generate Personalized Encoded Video", type="primary"):
        if source_video is None:
            if not use_project_raw_video:
                st.error("Please upload a source video first.")
                st.stop()

        files = {}
        if source_video is not None and not use_project_raw_video:
            files["source_video"] = (source_video.name, source_video.getvalue(), "video/mp4")
        data = {
            "viewer_login_id": viewer_login_id,
            "subscriber_name": subscriber_name,
            "device_id": device_id,
            "ip_address": ip_address,
            "segment_id": segment_id,
            "use_project_raw_video": str(use_project_raw_video).lower(),
            "project_raw_video_name": project_raw_video_name,
        }
        r = requests.post(f"{API_BASE}/portal/viewer/encode", data=data, files=files, timeout=600)
        if not r.ok:
            st.error(f"Encoding failed ({r.status_code}): {r.text}")
        else:
            result = r.json()
            st.session_state["latest_encode_response"] = result

            download_url = result["encoded_video_download_url"]
            if download_url.startswith("http://") or download_url.startswith("https://"):
                full_download_url = download_url
            else:
                full_download_url = f"{API_ROOT}{download_url}"

            download_response = requests.get(full_download_url, timeout=600)
            if not download_response.ok:
                st.error(
                    f"Encoded video created but download failed ({download_response.status_code}): {download_response.text}"
                )
            else:
                st.session_state["encoded_video_bytes"] = download_response.content
                st.session_state["encoded_video_name"] = result["encoded_video_name"]
                st.success("Personalized encoded video generated successfully.")

    if st.session_state["latest_encode_response"]:
        st.caption("Encoding metadata")
        st.json(st.session_state["latest_encode_response"])

    if st.session_state["encoded_video_bytes"]:
        st.caption("Encoded video preview")
        st.video(st.session_state["encoded_video_bytes"])
        st.download_button(
            label="Download Encoded Video",
            data=st.session_state["encoded_video_bytes"],
            file_name=st.session_state["encoded_video_name"] or "encoded_video.mp4",
            mime="video/mp4",
        )
        if st.button("Verify Last Encoded Video (Broadcaster Decode)"):
            files = {
                "encoded_video": (
                    st.session_state["encoded_video_name"] or "encoded_video.mp4",
                    st.session_state["encoded_video_bytes"],
                    "video/mp4",
                )
            }
            verify_response = requests.post(f"{API_BASE}/portal/broadcaster/decode", files=files, timeout=600)
            if not verify_response.ok:
                st.error(f"Verification failed ({verify_response.status_code}): {verify_response.text}")
            else:
                st.success("Verification complete and saved to database.")
                st.json(verify_response.json())

with broadcaster_tab:
    st.subheader("Broadcaster Upload and Decode")
    suspected_video = st.file_uploader(
        "Upload Encoded/Pirated Video for Forensic Decode",
        type=["mp4", "mov", "avi", "mkv"],
        key="broadcaster_video",
    )

    if suspected_video is not None:
        st.caption("Uploaded clip preview")
        st.video(suspected_video)

    if st.button("Decode and Save to Database", type="primary"):
        if suspected_video is None:
            st.error("Please upload a video for decoding.")
        else:
            files = {"encoded_video": (suspected_video.name, suspected_video.getvalue(), "video/mp4")}
            r = requests.post(f"{API_BASE}/portal/broadcaster/decode", files=files, timeout=600)
            if not r.ok:
                st.error(f"Decode failed ({r.status_code}): {r.text}")
            else:
                result = r.json()
                st.success("Decoded and saved in database.")
                st.json(result)
                if result.get("report_path"):
                    report_path = Path(result["report_path"])
                    if report_path.exists():
                        st.info(f"Forensic report generated: {report_path}")

    st.markdown("---")
    st.caption("Recent logged-in viewer sessions")
    session_limit = st.number_input("Max sessions to show", min_value=1, max_value=1000, value=50, step=1)
    if st.button("Refresh Session List"):
        r = requests.get(f"{API_BASE}/sessions", params={"limit": int(session_limit)}, timeout=30)
        if r.ok:
            sessions = r.json()
            st.write(f"Total sessions fetched: {len(sessions)}")
            st.json(sessions)
        else:
            st.error(r.text)

st.markdown("---")
st.caption("Each viewer upload gets a unique encoded payload. Broadcaster decode attempts attribution and stores evidence.")
