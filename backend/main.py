from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from rag.ingest import ingest_document
from rag.retriever import retrieve, retrieve_multi
from llm_api import chat_general_stream, chat_rag_stream, rewrite_queries, rerank_chunks, _build_context, get_model
from utils.router import auto_route
from utils.verifier import verify_answer
from utils.logger import log_query
import io

app = FastAPI(title="Hybrid RAG API v2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    query: str
    mode: str = "auto"       # "auto" | "rag" | "general"
    debug: bool = False
    history: list = []

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    ext = file.filename.split(".")[-1].lower()
    count = ingest_document(io.BytesIO(content), ext)
    return {"status": "success", "filename": file.filename, "chunks": count}

@app.post("/chat")
async def chat(req: ChatRequest):
    mode = req.mode if req.mode != "auto" else auto_route(req.query)

    if mode == "general":
        return StreamingResponse(chat_general_stream(req.query, req.history), media_type="text/plain")

    # ── RAG Pipeline ──────────────────────────────────────
    # 1. Multi-query rewrite (Disabled to dramatically speed up responses)
    rewrites = []
    all_queries = [req.query]

    # 2. Multi-query retrieval
    _, chunks = retrieve_multi(all_queries, k=5)

    # 3. Fallback if no doc
    if not chunks:
        return StreamingResponse(chat_general_stream(req.query, req.history), media_type="text/plain")

    # 5. Token-limited context
    context = _build_context(chunks, max_chars=3000)

    # 6. Generate answer (Streamed)
    return StreamingResponse(chat_rag_stream(req.query, context, req.history), media_type="text/plain")

@app.get("/health")
def health():
    return {"status": "ok"}
