import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def summarize_text(transcript, prompt=None):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        full_prompt = f"""
You are an AI meeting summarizer.
Summarize the following transcript into clearly separated sections:
1. Short Meeting Summary
2. Key Decisions
3. Action Items (Markdown checklist with [ ] boxes)

Transcript:
{transcript}

Extra instructions:
{prompt or 'None'}
"""

        response = model.generate_content(full_prompt)
        output = response.text.strip() if response and response.text else ""

        if not output:
            return "No summary generated.", "No action items found."

        action_match = re.search(
            r"(?:###|##|\d+\.|\*\*)?\s*Action Items[:\-\n]*([\s\S]+)", 
            output, 
            re.IGNORECASE
        )

        if action_match:
            actions = action_match.group(1).strip()
            summary = output[:action_match.start()].strip()
        else:
            summary = output
            actions = "No clear action items found."

        summary = re.sub(r"\n*\d+\.\s*$", "", summary)
        summary = re.sub(r"\n\s*\d+\.\s*\Z", "", summary)

        actions = f"### Action Items\n{actions}"

        return summary, actions

    except Exception as e:
        print("Summarization error:", e)
        return "Summarization failed.", "No action items."
