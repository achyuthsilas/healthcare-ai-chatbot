"""
Healthcare AI Chatbot — Streamlit UI
Run with: streamlit run app.py
"""
import os
import uuid
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from chatbot.llm import LLMClient
from chatbot.storage import ChatStorage
from chatbot.rag import KnowledgeBase

load_dotenv()

# ---------- Page config ----------
st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🩺",
    layout="centered",
)

DISCLAIMER = (
    "⚠️ **This assistant is for general information only and is NOT a "
    "substitute for professional medical advice, diagnosis, or treatment.** "
    "Always consult a licensed healthcare provider for medical concerns. "
    "If this is a medical emergency, call your local emergency number."
)

# ---------- Initialize services (cached so they don't reload on every rerun) ----------
@st.cache_resource
def get_services():
    storage = ChatStorage(db_path="chat_history.db")
    knowledge = KnowledgeBase(docs_dir="data")
    llm = LLMClient()
    return storage, knowledge, llm


storage, knowledge, llm = get_services()

# ---------- Session state ----------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Sidebar ----------
with st.sidebar:
    st.header("🩺 Healthcare AI")
    st.caption("Powered by AI")
    st.divider()

    if st.button("🆕 New conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Past sessions")
    sessions = storage.list_sessions(limit=10)
    if not sessions:
        st.caption("No past conversations yet.")
    for sess_id, first_msg, ts in sessions:
        label = (first_msg[:35] + "…") if len(first_msg) > 35 else first_msg
        if st.button(f"💬 {label}", key=sess_id, use_container_width=True):
            st.session_state.session_id = sess_id
            st.session_state.messages = storage.get_messages(sess_id)
            st.rerun()

    st.divider()
    st.caption(f"Session ID: `{st.session_state.session_id[:8]}…`")

# ---------- Main UI ----------
st.title("🩺 Healthcare AI Assistant")
st.info(DISCLAIMER)

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a health question…"):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Persist user message
    storage.save_message(
        session_id=st.session_state.session_id,
        role="user",
        content=prompt,
        timestamp=datetime.utcnow().isoformat(),
    )

    # 3. Retrieve relevant context from knowledge base (RAG)
    context_chunks = knowledge.search(prompt, top_k=3)
    context_text = "\n\n".join(context_chunks) if context_chunks else ""

    # 4. Generate assistant response (streaming)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            for chunk in llm.stream_response(
                messages=st.session_state.messages,
                context=context_text,
            ):
                full_response += chunk
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ Error: {e}"
            placeholder.error(full_response)

    # 5. Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    storage.save_message(
        session_id=st.session_state.session_id,
        role="assistant",
        content=full_response,
        timestamp=datetime.utcnow().isoformat(),
    )
