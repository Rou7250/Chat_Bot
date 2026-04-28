import pickle
import os
from rank_bm25 import BM25Okapi

STORE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "store")

def _get_bm25_and_chunks():
    meta_path = os.path.join(STORE, "meta.pkl")
    if not os.path.exists(meta_path):
        return None, []
    try:
        with open(meta_path, "rb") as f:
            chunks = pickle.load(f)
        if not chunks:
            return None, []
        tokenized_corpus = [chunk.lower().split() for chunk in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        return bm25, chunks
    except Exception:
        return None, []

def retrieve(query: str, k: int = 4) -> tuple[str, list[str], list[float]]:
    bm25, chunks = _get_bm25_and_chunks()
    if not bm25 or not chunks:
        return "", [], []
    
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query).tolist()
    
    # Get top k indices
    top_k_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    
    top_chunks = [chunks[i] for i in top_k_indices]
    top_scores = [scores[i] for i in top_k_indices]
    
    return "\n\n".join(top_chunks), top_chunks, top_scores

def retrieve_multi(queries: list[str], k: int = 3) -> tuple[str, list[str]]:
    bm25, chunks = _get_bm25_and_chunks()
    if not bm25 or not chunks:
        return "", []
        
    seen, merged = set(), []
    for q in queries:
        tokenized_query = q.lower().split()
        scores = bm25.get_scores(tokenized_query).tolist()
        top_k_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        for i in top_k_indices:
            c = chunks[i]
            key = c[:80]
            if key not in seen:
                seen.add(key)
                merged.append(c)
                
    return "\n\n".join(merged), merged
