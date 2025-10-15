import streamlit as st
from utils.transcription import transcribe_audio
from utils.summarize import summarize_text
from utils.database import save_to_db
from utils.files import generate_downloads
import os
import re

# --- Page setup ---
st.set_page_config(page_title="Meeting Summarizer", layout="wide", page_icon="🔘")

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .scroll-box {
        border: 1px solid #444;
        padding: 12px;
        border-radius: 10px;
        height: 450px;
        overflow-y: auto;
        background-color: #1e1e1e;
        color: #eee;
        white-space: pre-wrap;
    }
    .stDownloadButton>button {
        background-color: #21ba45 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }
    .stDownloadButton>button:hover {
        background-color: #16ab39 !important;
    }

    div[data-baseweb="tab"] > button > p {
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("Meeting Summarizer")

# --- Layout ---
left_col,spacer, right_col = st.columns([2, 0.3,3])

# ----------------------------
# LEFT PANEL
# ----------------------------
with left_col:
    st.header("📂 Upload file")

    audio_file = st.file_uploader("Select your meeting audio", type=["mp3", "wav"])
    prompt = st.text_area(" ", placeholder="Enter prompt")

    if st.button("Process Audio"):
        if not audio_file:
            st.warning("Please upload an audio file first.")
            st.stop()

        # --- Transcription ---
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio(audio_file)
            if not transcript:
                st.error("Transcription failed. Try Again.")
                st.stop()
        st.success("Transcription completed")

        # --- Summarization ---
        with st.spinner("Summarizing content..."):
            summary, action_items = summarize_text(transcript, prompt)

        # 🔹 Clean summary formatting
        summary = re.sub(r"\n*\d+\.\s*$", "", summary.strip())  # remove lonely trailing numbers
        summary = re.sub(r"\n\s*\d+\.\s*\Z", "", summary)       # remove section-ending digits

        st.success("Summary generated!")

        # --- Save to DB ---
        save_to_db(audio_file.name, transcript, summary, action_items)
        

        # --- Generate download files ---
        pdf_file, docx_file, md_file = generate_downloads(audio_file.name, transcript, summary, action_items)

        st.session_state.update({
            "audio_name": os.path.splitext(audio_file.name)[0],
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "files": {
                "pdf": pdf_file,
                "docx": docx_file,
                "md": md_file
            }
        })

# ----------------------------
# RIGHT PANEL
# ----------------------------
with right_col:
    st.header("Preview")

    if "transcript" in st.session_state:
        transcript = st.session_state["transcript"]
        summary = st.session_state["summary"]
        action_items = st.session_state["action_items"]
        audio_name = st.session_state["audio_name"]
        files = st.session_state["files"]

        tab1, tab2, tab3 = st.tabs(["Transcript", "Summary", "Action Items"])

        # --- Transcript Tab ---
        with tab1:
            st.markdown("### Transcript")
            st.markdown(f"<div class='scroll-box'>{transcript}</div>", unsafe_allow_html=True)

        # --- Summary Tab ---
        with tab2:
            st.markdown("### Summary")
            st.markdown(f"<div class='scroll-box'>{summary}</div>", unsafe_allow_html=True)

        # --- Action Items Tab (render markdown properly) ---
        with tab3:
            if action_items:
                import markdown

                # Convert Markdown to HTML and wrap inside one HTML block
                action_html = markdown.markdown(action_items, extensions=['extra', 'nl2br'])

                full_html = f"""
                <div style='border:1px solid #444; padding:12px; border-radius:10px;
                            background-color:#1e1e1e; color:#eee;
                            overflow-y:auto; max-height:450px;'>
                    {action_html}
                </div>
                """

                st.markdown(full_html, unsafe_allow_html=True)
            else:
                st.info("No action items found.")



        # --- Download section ---
        with left_col:
            st.subheader("Download File")

            file_type = st.selectbox(
                "Select file type",
                options=["PDF", "Word", "Markdown"],
                index=0
            )

            file_map = {
                "PDF": ("pdf", "application/pdf"),
                "Word": ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                "Markdown": ("md", "text/markdown")
            }

            ext, mime = file_map[file_type]
            file_path = files[ext]
            download_name = f"{audio_name}.{ext}"

            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {file_type}",
                    data=f,
                    file_name=download_name,
                    mime=mime
                )

    else:
        st.info("Upload and process a meeting audio to preview transcript, summary, and actions.")
