# 🧠 Hybrid RAG Chatbot v2

A modern, highly-polished generative AI chatbot application. This project features a sophisticated **Retrieval-Augmented Generation (RAG)** engine for answering questions based on your personal documents (PDFs/TXTs), alongside a standard conversational AI interface—all powered by **Groq** and Meta's **Llama 3 70B** model.

The application architecture is strictly decoupled into a **Streamlit** frontend dashboard and a **FastAPI** backend API.

---

## ✨ Features

- **Hybrid Routing Network:** Automatically routes your query to the correct system. If you ask a general question, it chats with you naturally. If you ask about a document, it queries the vector database.
- **Advanced RAG Pipeline:** Employs Multi-Query rewriting, Context Reranking, and fallback mechanisms to ensure the highest quality retrieval accuracy.
- **ChatGPT-Style Persistent History:** Never lose a conversation. Your chat history is permanently stored in `chats.json` allowing you to seamlessly hop back into older conversations via the sidebar.
- **Premium Glassmorphic UI:** A heavily customized, beautiful dark-theme Streamlit dashboard specifically optimized for usability and aesthetics.

---

## 🏗️ Architecture

The project contains two independent layers:
- `backend/`: Contains the intelligent FastAPI server, the RAG engine (FAISS document ingestion/retrieval), the intelligent Router, and the Groq LLM integration.
- `frontend/`: Contains the `app.py` Streamlit dashboard UI, session management logic, and local data persistence.

---

## 🛠️ Technology Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (via custom CSS injections for modern design)
- **Backend API:** [FastAPI](https://fastapi.tiangolo.com/) with Uvicorn
- **AI / LLM Provider:** [Groq API](https://groq.com/) for LPU-accelerated inference
- **Core LLM Model:** `llama-3.3-70b-versatile` (Meta's Llama 3)
- **Vector Database:** [FAISS](https://github.com/facebookresearch/faiss) (Facebook AI Similarity Search)
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Data Persistence:** Local JSON storage (`chats.json`)

---

## 🚀 Setup & Installation

### 1. Requirements
Ensure you have Python installed, then install the fundamental dependencies:
```bash
pip install fastapi uvicorn streamlit requests groq
```

### 2. API Keys
You must provide a valid API key for Groq to power inference.
Create a `.env` file inside **both** the `frontend/` and `backend/` directories, and add the following line:
```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 💻 Running the Application

Because the architecture has been professionalized into a two-tier system, you must run both layers independently in two separate terminal windows.

### Step 1: Start the Backend API
This server handles all intelligence, document chunks, and AI requests.
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 2: Start the Frontend UI
This runs the beautiful dashboard that you will actually interact with via your web browser.
```bash
cd frontend
streamlit run app.py
```

The application will automatically pop open in your browser at `http://localhost:8501`. Happy chatting!
