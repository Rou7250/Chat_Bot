import os
import pickle
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

STORE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "store")

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
        
    # Append to existing chunks if any
    existing_chunks = []
    meta_path = os.path.join(STORE, "meta.pkl")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "rb") as f:
                existing_chunks = pickle.load(f)
        except Exception:
            pass
            
    all_chunks = existing_chunks + chunks
    
    with open(meta_path, "wb") as f:
        pickle.dump(all_chunks, f)
        
    return len(chunks)
