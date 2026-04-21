import os
import faiss
import pickle
import numpy as np
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

MODEL = None
STORE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "store")

def get_model():
    global MODEL
    if MODEL is None:
        from sentence_transformers import SentenceTransformer
        MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return MODEL

def ingest_document(file_obj, ext):
    os.makedirs(STORE, exist_ok=True)
    text = ""
    if ext == "pdf":
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    elif ext in ("txt", "md"):
        text = file_obj.read().decode("utf-8", errors="ignore")
    
    if not text.strip():
        return 0
        
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    chunks = splitter.split_text(text)
    
    if not chunks:
        return 0
        
    model = get_model()
    vecs = model.encode(chunks).astype(np.float32)
    
    index = faiss.IndexFlatL2(vecs.shape[1])
    index.add(vecs)
    
    faiss.write_index(index, f"{STORE}/faiss.index")
    with open(f"{STORE}/meta.pkl", "wb") as f:
        pickle.dump(chunks, f)
        
    return len(chunks)
