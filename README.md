# 🧠 RagFlow
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/Streamlit-UI-red?logo=streamlit" />
  <img src="https://img.shields.io/badge/RAG-FAISS%20%7C%20LangChain-brightgreen" />
  <img src="https://img.shields.io/badge/LLM-Google%20Gemini-orange" />
  <img src="https://img.shields.io/badge/Status-Active%20Development-success" />
</p>

**RAGFlow** is a clean, modular, production-style conversational AI application built with  
**Retrieval-Augmented Generation (RAG)**.

It enables **document-grounded conversations**, **multi-chat sessions**, **streaming responses**, **persona selection**, and **multilingual output** — with a **cleanly separated backend and frontend**.



## 🖼️ Application Preview

![RAGFlow UI](assets/ui.png)



## ✨ Key Features

### 🏗 Clean Architecture
- Fully separated **backend** and **frontend**
- Backend can run independently (CLI today, API-ready for the future)
- Clear service boundaries for maintainability and scaling



### 📄 Retrieval-Augmented Generation (RAG)
- Upload documents: **PDF, TXT, DOCX, CSV**
- Automatic text extraction, chunking, and embedding
- **FAISS-based vector search** for fast, relevant retrieval
- Per-chat document isolation (no context leakage)



### 💬 Chat Experience
- Multi-chat sessions (create, switch, rename)
- Each chat maintains its **own history and context**
- Token-by-token **streaming responses** for real-time UX



### 🎭 Personalization & Language
- Built-in personas:
  - Friendly Assistant
  - Formal Expert
  - Tech Support
- Multilingual responses:
  - English
  - Urdu
  - Arabic


## 🗂️ Project Structure 

```text
ragflow-chat/
├── backend/                       # Core backend (frontend-agnostic)
│   ├── __init__.py                # Package marker
│   ├── config.py                  # Central config (chunk sizes, model names, etc.)
│   ├── model.py                   # LLM + embeddings initialization (Gemini)
│   ├── graph.py                   # LangGraph workflow / orchestration
│   ├── chat_service.py            # High-level streaming chat service (UI/CLI call this)
│   ├── rag.py                     # Retrieval service (query → relevant context)
│   └── document_rag.py            # Document ingestion: extract → chunk → embed → FAISS
│
├── frontend/                      # Streamlit frontend (UI only)
│   ├── streamlit_app.py           # UI entrypoint (wires sidebar + chat UI)
│   ├── sidebar.py                 # Sidebar UI: chats list, RAG upload, settings, actions
│   ├── chat_ui.py                 # Chat rendering + streaming response display
│   └── state.py                   # Session-state helpers (new chat, rename, safe indexes)
│
├── scripts/                       # Backend-only utilities (no Streamlit required)
│   ├── chat_cli.py                # CLI chat (persona + language; no document RAG)
│   └── rag_cli.py                 # CLI RAG: loads a local document path, then Q&A
│
├── assets/
│   └── ui.png                     # Screenshot used by README (optional but recommended)
│
├── .streamlit/
│   └── secrets.toml               # Local API keys (DO NOT COMMIT)
│
├── requirements.txt               # Python dependencies
├── .gitignore                     # Ignore venv, secrets, caches, etc.
└── README.md                      # Project documentation
```



## 🧰 Tech Stack

- **Python 3.11+**
- **Streamlit** (UI)
- **LangChain + LangGraph** (orchestration)
- **Google Gemini** (LLM + embeddings)
- **FAISS** (vector search)
- **PyPDF2 / python-docx / pandas** (document parsing)



## ⚙️ Setup

### 1) Create a virtual environment

```bash
python -m venv venv
```

Activate:

- **Windows (PowerShell)**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**
  ```bash
  source venv/bin/activate
  ```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Add secrets

Create:

`.streamlit/secrets.toml`

```toml
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
```

> This file is ignored by Git and should stay local.



## ▶️ Run the Streamlit UI

```bash
streamlit run frontend/streamlit_app.py
```

Open:

- http://localhost:8501



## 💬 Run Chat CLI (backend-only)

Runs the chatbot in your terminal (no Streamlit).

```bash
python scripts/chat_cli.py
```



## 🧪 Run RAG CLI (backend-only)

This runs RAG entirely in your terminal.

```bash
python scripts/rag_cli.py
```

### How “document upload” works in the CLI

In `rag_cli.py`, you **provide a local file path** when prompted (that’s the “upload” step for CLI).  
Supported formats: `pdf`, `txt`, `docx`, `csv`

The CLI will then:
1. Read the file from disk
2. Extract text
3. Chunk text (overlapping chunks)
4. Create embeddings
5. Build an in-memory FAISS index
6. Let you ask questions grounded in the document

**Notes**
- Vector store is **in-memory** (not persisted)
- Each run creates a **fresh** index


## 🚀 Future Improvements

- Persist vector stores (disk/DB) per user/chat
- Add FastAPI backend for web/mobile clients
- Authentication + user accounts
- Dockerization / deployment templates
- Better document parsing (OCR for scanned PDFs)



## 👤 Author

Built by **Sajid Ali**  
Focused on clean architecture, RAG systems, and maintainable AI applications.
