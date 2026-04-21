import logging, json, os
from datetime import datetime

os.makedirs("utils/logs", exist_ok=True)

logging.basicConfig(
    filename="utils/logs/rag.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def log_query(original: str, rewrites: list, chunks: list, answer: str, confidence: str, mode: str):
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "mode": mode,
        "original_query": original,
        "rewritten_queries": rewrites,
        "retrieved_chunks": chunks,
        "answer": answer[:300],
        "confidence": confidence,
    }
    logging.info(json.dumps(entry))
    return entry
