import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("==========================================================")
    print("CRITICAL WARNING: GROQ_API_KEY is missing in Render Environment!")
    print("==========================================================")
    client = None
else:
    client = Groq(api_key=api_key)

MODEL_NAME = "llama-3.3-70b-versatile"

_RAG_PROMPT = (
    "Answer ONLY using the context below.\n"
    "If not found, say exactly: 'Answer not found in the document.'\n\n"
    "Context:\n{context}\n\nQuestion: {query}"
)
_GENERAL_PROMPT_SYS = "Answer professionally and use full sentences. Be helpful but concise."
_REWRITE_PROMPT = (
    "Generate 2 alternative search queries for: '{query}'\n"
    "Return ONLY a JSON array of 2 strings. No extra text."
)
_RERANK_PROMPT = (
    "Given the question: '{query}'\n"
    "Rank these chunks by relevance (most relevant first).\n"
    "Return ONLY a JSON array of indices (0-based).\n\n"
    "Chunks:\n{chunks}"
)

def _call(prompt: str, system_prompt: str = "") -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.0
    )
    return response.choices[0].message.content

def rewrite_queries(query: str) -> list[str]:
    try:
        raw = _call(_REWRITE_PROMPT.format(query=query))
        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return []

def rerank_chunks(query: str, chunks: list[str]) -> list[str]:
    if len(chunks) <= 1:
        return chunks
    try:
        numbered = "\n\n".join(f"[{i}] {c[:300]}" for i, c in enumerate(chunks))
        raw = _call(_RERANK_PROMPT.format(query=query, chunks=numbered))
        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if match:
            indices = json.loads(match.group())
            return [chunks[i] for i in indices if i < len(chunks)]
    except Exception:
        pass
    return chunks

def _build_context(chunks: list[str], max_chars: int = 3000) -> str:
    ctx, total = [], 0
    for chunk in chunks:
        if total + len(chunk) > max_chars:
            break
        ctx.append(chunk)
        total += len(chunk)
    return "\n\n".join(ctx)

def _call_stream(messages: list):
    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
            temperature=0.2
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as exc:
        yield f"⚠️ [Groq API Error: {str(exc)}]"

def chat_rag_stream(query: str, context: str, history: list = None):
    messages = []
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    prompt = _RAG_PROMPT.format(context=context, query=query)
    messages.append({"role": "user", "content": prompt})
    yield from _call_stream(messages)

def chat_general_stream(query: str, history: list = None):
    messages = [{"role": "system", "content": _GENERAL_PROMPT_SYS}]
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})
    yield from _call_stream(messages)

class MockGeminiModel:
    def generate_content(self, prompt: str):
        class Response:
            def __init__(self, text):
                self.text = text
        return Response(_call(prompt))

def get_model():
    return MockGeminiModel()
