import json
import os
import uuid
from datetime import datetime

STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chats.json")

def load_all_chats() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_chat(chat_id: str, messages: list):
    chats = load_all_chats()
    
    # Determine title from the first user message
    title = "New Chat"
    for m in messages:
        if m["role"] == "user":
            title = m["content"][:30] + ("..." if len(m["content"]) > 30 else "")
            break
            
    chats[chat_id] = {
        "title": title,
        "messages": messages,
        "updated_at": datetime.now().isoformat()
    }
    
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2)

def generate_chat_id() -> str:
    return str(uuid.uuid4())

def clear_all_chats():
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)
