import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def summarize_text(transcript, prompt=None):
    try:
        # ✅ Use supported model name
        model = genai.GenerativeModel("gemini-2.5-flash")

        full_prompt = f"""
You are an AI meeting summarizer.
Summarize the following transcript into:
1. A short meeting summary
2. Key decisions
3. Action items (Markdown checklist)

Transcript:
{transcript}

Extra instructions:
{prompt or 'None'}
"""

        response = model.generate_content(full_prompt)
        output = response.text

        if not output:
            return "No summary generated.", "No action items found."

        # Simple parsing
        if "Action Items" in output:
            parts = output.split("Action Items", 1)
            summary = parts[0].strip()
            actions = "### Action Items\n" + parts[1].strip()
        else:
            summary, actions = output, "No clear action items found."

        return summary, actions

    except Exception as e:
        print("Summarization error:", e)
        return "Summarization failed.", "No action items."
