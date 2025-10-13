import streamlit as st
from utils.transcription import transcribe_audio
from utils.summarize import summarize_text
from utils.database import save_to_db
import os

st.set_page_config(page_title="Meeting Summarizer", layout="wide")
st.title("🧠 Meeting Summarizer")

st.write("Upload your meeting audio and get a smart summary with action items.")

# File upload
audio_file = st.file_uploader("Upload meeting audio", type=["mp3", "wav"])
prompt = st.text_area("Optional Prompt", placeholder="E.g., Summarize in bullet points with action items...")

if st.button("Process Audio"):
    if audio_file is not None:
        with st.spinner("🔊 Transcribing audio using AssemblyAI..."):
            transcript = transcribe_audio(audio_file)
            if not transcript:
                st.error("Transcription failed. Check logs or API key.")
                st.stop()

        st.subheader("📝 Transcript")
        st.text_area("Full Transcript", transcript, height=200)

        with st.spinner("🤖 Generating summary using Gemini..."):
            summary, actions = summarize_text(transcript, prompt)

        st.subheader("📋 Summary")
        st.markdown(summary)

        st.subheader("✅ Action Items")
        st.markdown(actions)

        save_to_db(audio_file.name, transcript, summary, actions)
        st.success("✅ Summary saved successfully to MongoDB!")
    else:
        st.warning("Please upload an audio file first.")
