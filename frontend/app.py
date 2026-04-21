import streamlit as st
import requests
import os
from utils.chat_storage import load_all_chats, save_chat, generate_chat_id, clear_all_chats

API = os.getenv("BACKEND_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Hybrid RAG Chatbot v2", page_icon="🧠", layout="wide")

st.markdown("""
<style>
/* Import premium typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit default branding & menus */
header {background-color: transparent !important;}
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
.stDeployButton {display: none !important;}

/* Elegant Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #13111C 0%, #171626 50%, #1E1C3A 100%);
    color: #F8F8F2;
}

/* Sleek Sidebar */
[data-testid="stSidebar"] {
    background-color: #0D0C14 !important;
    border-right: 1px solid #232136;
}

/* Button Styling */
button[kind="secondary"] {
    background-color: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    font-weight: 500 !important;
}
button[kind="secondary"]:hover {
    background-color: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
    transform: translateY(-1px);
}

/* Styling the input text bar */
[data-testid="stChatInput"] {
    background-color: rgba(20, 20, 35, 0.8) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

/* Styling the chat bubbles */
[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 10px 15px;
}
</style>
""", unsafe_allow_html=True)

# ── State Initialization ─────────────────────────────────────
if "chat_id" not in st.session_state:
    st.session_state.chat_id = generate_chat_id()
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    if st.button("📝 New chat", use_container_width=True):
        st.session_state.chat_id = generate_chat_id()
        st.session_state.messages = []
        st.rerun()

    st.subheader("Recents")
    
    chats = load_all_chats()
    
    # Sort chats by updated_at descending
    sorted_chats = sorted(chats.items(), key=lambda x: x[1].get("updated_at", ""), reverse=True)
    
    for cid, chat_data in sorted_chats:
        if st.button(chat_data["title"], key=f"btn_{cid}", use_container_width=True):
            st.session_state.chat_id = cid
            st.session_state.messages = chat_data["messages"]
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear History", use_container_width=True):
        clear_all_chats()
        st.session_state.chat_id = generate_chat_id()
        st.session_state.messages = []
        st.rerun()

# ── Chat ──────────────────────────────────────────────────
user_input = st.chat_input("Ask a question...", accept_file="multiple", file_type=["pdf", "txt"])

# Don't show the standard title if empty so we can show the hero dashboard
if len(st.session_state.messages) > 0 or user_input:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
else:
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Hi, I'm Chat Bot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ccc;'>Tell me your goal, and get complete Learning Plans.</p>", unsafe_allow_html=True)
    st.write("<br><p style='text-align: center; color: #aaa; font-style: italic;'>Here is what You'll get</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("#### 🧩 Guided Learning")
            st.caption("15%")
    with col2:
        with st.container(border=True):
            st.markdown("#### 🔗 Links To Course")
            st.caption("63%")
    with col3:
        with st.container(border=True):
            st.markdown("#### 💾 Save Courses")
            st.caption("41%")
            
    col4, col5, col6 = st.columns(3)
    with col4:
        with st.container(border=True):
            st.markdown("#### 💬 Chat Wit AI")
            st.caption("15%")
    with col5:
        with st.container(border=True):
            st.markdown("#### 🎯 Learning Plans")
            st.caption("63%")
    with col6:
        with st.container(border=True):
            st.markdown("#### 📄 Download PDFs")
            st.caption("41%")
if user_input:
    # 1. Provide fallback if user's streamlit is too old
    query = getattr(user_input, "text", user_input) if hasattr(user_input, "text") else user_input
    files = getattr(user_input, "files", []) if hasattr(user_input, "files") else []

    # 2. Upload any attached files seamlessly
    for f in files:
        with st.spinner(f"Ingesting {f.name}..."):
            res = requests.post(f"{API}/upload", files={"file": (f.name, f.getvalue())})
        if res.ok:
            st.session_state.doc_loaded = True
            st.toast(f"✅ Ingested {f.name} successfully!")
            # Add a system message locally so the user knows it happened
            msg = {"role": "assistant", "content": f"I have ingested your document: **{f.name}**."}
            st.session_state.messages.append(msg)
            save_chat(st.session_state.chat_id, st.session_state.messages)
            
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
        else:
            st.toast(f"⚠️ Failed to ingest {f.name}")

    # 3. Process the text query if present
    if isinstance(query, str) and query.strip():
        st.session_state.messages.append({"role": "user", "content": query})
        save_chat(st.session_state.chat_id, st.session_state.messages)
        
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    history_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:] if m["role"] in ("user", "assistant")]
                    res = requests.post(
                        f"{API}/chat",
                        json={"query": query, "mode": "auto", "debug": False, "history": history_payload},
                        timeout=45,
                        stream=True
                    )
                    res.raise_for_status()
                    
                def generate():
                    for chunk in res.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk: yield chunk
                reply = st.write_stream(generate())
            except Exception as e:
                reply = f"⚠️ {e}"
                st.markdown(reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
        save_chat(st.session_state.chat_id, st.session_state.messages)
