from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["meeting_summarizer"]
collection = db["summaries"]

def save_to_db(file_name, transcript, summary, actions):
    try:
        data = {
            "file_name": file_name,
            "transcript": transcript,
            "summary": summary,
            "action_items": actions,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(data)
        print("Saved to MongoDB successfully!")
    except Exception as e:
        print("MongoDB save error:", e)
