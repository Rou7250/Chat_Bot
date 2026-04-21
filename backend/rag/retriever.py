import faiss, pickle, numpy as np, os
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
STORE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "store")

def _search(vec: np.ndarray, k: int):
    idx_path = f"{STORE}/faiss.index"
    if not os.path.exists(idx_path):
        return [], []
    index = faiss.read_index(idx_path)
    with open(f"{STORE}/meta.pkl", "rb") as f:
        chunks = pickle.load(f)
    distances, I = index.search(vec, min(k, len(chunks)))
    return [chunks[i] for i in I[0] if i < len(chunks)], distances[0].tolist()

def retrieve(query: str, k: int = 4) -> tuple[str, list[str], list[float]]:
    vec = MODEL.encode([query]).astype(np.float32)
    chunks, scores = _search(vec, k)
    return "\n\n".join(chunks), chunks, scores

def retrieve_multi(queries: list[str], k: int = 3) -> tuple[str, list[str]]:
    seen, merged = set(), []
    for q in queries:
        vec = MODEL.encode([q]).astype(np.float32)
        chunks, _ = _search(vec, k)
        for c in chunks:
            key = c[:80]
            if key not in seen:
                seen.add(key)
                merged.append(c)
    return "\n\n".join(merged), merged
