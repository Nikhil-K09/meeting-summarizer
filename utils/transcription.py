import requests
import os
from dotenv import load_dotenv

load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

HEADERS = {"authorization": ASSEMBLYAI_API_KEY}

def transcribe_audio(audio_file):
    try:
        upload_url = "https://api.assemblyai.com/v2/upload"
        response = requests.post(upload_url, headers=HEADERS, data=audio_file)
        response.raise_for_status()
        audio_url = response.json()["upload_url"]

        transcript_request = {"audio_url": audio_url}
        transcript = requests.post("https://api.assemblyai.com/v2/transcript", json=transcript_request, headers=HEADERS)
        transcript_id = transcript.json()["id"]

        while True:
            status = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=HEADERS).json()
            if status["status"] == "completed":
                return status["text"]
            elif status["status"] == "error":
                print("Error:", status["error"])
                return None
    except Exception as e:
        print("Transcription error:", e)
        return None
