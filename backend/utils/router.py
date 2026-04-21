import json
import re
from llm_api import get_model

_ROUTER_PROMPT = """You are a smart query classifier. 
Your job is to determine whether the user is asking a "general" knowledge question / greeting, or if they are asking a "rag" question that requires looking up information from their uploaded document.

IMPORTANT: The user may make typos (e.g., "hellop" instead of "hello", "capitl" instead of "capital"). You must silently correct these typos in your head and route based on what they MEANT to say.

Examples of "general":
- "What is the capital of Bihar?"
- "Hello" / "Hi" / "hellop" / "hey"
- "Who is the president?"
- "Explain quantum computing."

Examples of "rag" (Document Q&A):
- "What is my 10th percentage?"
- "What is my name?"
- "What are my skills?"
- "Summarize this document"
- "Where did I work previously?"

User Query:
{query}

Respond ONLY as a JSON dictionary with a single key "route" mapped to either "general" or "rag".
"""

def auto_route(query: str) -> str:
    try:
        model = get_model()
        res = model.generate_content(_ROUTER_PROMPT.format(query=query))
        text = res.text.strip()
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            route = json.loads(match.group()).get("route", "rag").lower()
            if route in ["general", "rag"]:
                return route
    except Exception:
        pass
    
    # Safest default is to try looking it up in the document
    return "rag"
