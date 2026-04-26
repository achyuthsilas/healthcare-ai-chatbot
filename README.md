# 🩺 Healthcare AI Chatbot

A streaming chatbot that answers general health questions using **Groq's free Llama API** (Llama 3.3 70B), with **persistent chat history** (SQLite) and a lightweight **RAG layer** (TF-IDF over local Markdown files).

> ⚠️ For information only. Not a substitute for professional medical advice.

---

## ✨ Features

- 💬 Streaming chat UI built with Streamlit
- 🧠 Groq LLM (Llama 3.3 70B) — fast inference, generous free tier
- 💾 SQLite chat history — every conversation is saved and resumable
- 📚 Simple TF-IDF RAG over Markdown/TXT files in `data/`
- 🔒 API key loaded from `.env` (never committed)
- ✅ Pytest suite for the storage layer

---

## 📁 Project structure

```
healthcare-chatbot/
├── app.py                  # Streamlit entry point
├── chatbot/
│   ├── __init__.py
│   ├── llm.py              # Claude API wrapper (streaming)
│   ├── storage.py          # SQLite chat persistence
│   └── rag.py              # TF-IDF document retrieval
├── data/
│   └── health_info.md      # Sample knowledge base
├── tests/
│   └── test_storage.py
├── .streamlit/
│   └── config.toml
├── .env.example
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Quick start

### 1. Clone and enter the repo

```bash
git clone https://github.com/<your-username>/healthcare-chatbot.git
cd healthcare-chatbot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key (free!)

Get a free key at <https://console.groq.com/keys> — no credit card required. Then:

```bash
cp .env.example .env
# open .env and replace the placeholder with your real key
```

### 5. Run the app

```bash
streamlit run app.py
```

Open <http://localhost:8501> in your browser. 🎉

---

## 🧪 Run tests

```bash
pytest
```

---

## 📚 Adding to the knowledge base

Drop `.md` or `.txt` files into the `data/` directory and restart the app. They'll automatically be chunked, indexed, and used for retrieval-augmented answers.

---

## 🔧 Customization ideas

- **Different LLM** — swap `chatbot/llm.py` for OpenAI, Claude, Gemini, or a local Ollama model
- **Different model** — change `DEFAULT_MODEL` in `chatbot/llm.py` (try `llama-3.1-8b-instant` for speed)
- **Better RAG** — replace TF-IDF with ChromaDB / FAISS + embeddings
- **Auth** — add Streamlit's native auth or wrap behind a reverse proxy
- **Different domain** — change `SYSTEM_PROMPT` in `chatbot/llm.py` and replace the `data/` files. The architecture works for legal Q&A, customer support, study buddy, etc.

---

## 🌐 Deploy free on Streamlit Community Cloud

1. Push the repo to GitHub (instructions below)
2. Go to <https://share.streamlit.io>
3. Connect your GitHub, pick the repo, set `app.py` as the entry point
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
5. Click Deploy. Done.

---

## 📜 License

MIT — see [LICENSE](LICENSE).

---

## ⚠️ Medical disclaimer

This software is provided for educational and informational purposes only. It is **not** a medical device and is **not** intended to diagnose, treat, cure, or prevent any disease. Always seek the advice of a qualified health provider with any questions you may have regarding a medical condition.
