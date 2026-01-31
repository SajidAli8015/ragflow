# scripts/rag_cli.py
import os
import sys
import time
from pathlib import Path

# --- Fix import path ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# --- Load secrets from .streamlit/secrets.toml ---
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    raise RuntimeError("Python 3.11+ is required for tomllib")

SECRETS_PATH = ".streamlit/secrets.toml"
if not os.path.exists(SECRETS_PATH):
    raise FileNotFoundError(
        f"Secrets file not found at {SECRETS_PATH}. "
        "Make sure .streamlit/secrets.toml exists."
    )

with open(SECRETS_PATH, "rb") as f:
    secrets = tomllib.load(f)

os.environ["GOOGLE_API_KEY"] = secrets["GOOGLE_API_KEY"]
os.environ["LANGSMITH_API_KEY"] = secrets.get("LANGSMITH_API_KEY", "")

# --- Backend imports (after env vars are set) ---
from backend.model import get_chat_model
from backend.graph import build_graph
from backend.chat_service import ChatService
from backend.document_rag import extract_text, compute_file_hash
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


def build_rag_vectorstore_from_path(file_path: str):
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    print("\n[1/4] Reading file...")
    file_bytes = path.read_bytes()
    print(f"      Size: {len(file_bytes) / (1024 * 1024):.2f} MB")

    print("[2/4] Extracting text...")
    raw_text = extract_text(file_bytes, path.name)
    print(f"      Extracted: {len(raw_text):,} characters")

    if not raw_text.strip():
        raise ValueError("No text extracted from document (PDF may be scanned/image-only).")

    print("[3/4] Chunking text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(raw_text)
    print(f"      Chunks: {len(chunks)} (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    print("[4/4] Creating embeddings + FAISS index (this can take a while)...")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)

    # Small heartbeat so it doesn't look frozen
    start = time.time()
    last_ping = start

    # FAISS.from_texts will call embeddings internally; we ping occasionally
    # by wrapping in a simple timer loop around the call.
    # (We can't easily stream per-chunk progress without rewriting FAISS build.)
    vs = None
    try:
        vs = FAISS.from_texts(chunks, embedding=embeddings)
    finally:
        now = time.time()
        elapsed = now - start
        print(f"      Done. Time: {elapsed:.1f}s")

    file_hash = compute_file_hash(file_bytes)
    return vs, path.name, file_hash


def main():
    print("\n🤖 RAG CLI (backend-only)")
    print("Type 'exit' or 'quit' to stop.\n")

    file_path = input("Enter document path (pdf/txt/docx/csv): ").strip().strip('"')
    if file_path.lower() in {"exit", "quit"}:
        return

    try:
        vectorstore, filename, _ = build_rag_vectorstore_from_path(file_path)
    except Exception as e:
        print(f"\n❌ Failed to build RAG index: {e}\n")
        return

    print(f"\n✅ Loaded + embedded: {filename}\n")

    persona = input("Persona [Friendly Assistant / Formal Expert / Tech Support] (default: Friendly Assistant): ").strip()
    if not persona:
        persona = "Friendly Assistant"

    language = input("Language [English / Urdu / Arabic] (default: English): ").strip()
    if not language:
        language = "English"

    # Init backend
    model = get_chat_model()
    graph = build_graph(model)
    chat_service = ChatService(graph)

    session_id = "rag-cli-session"

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye 👋")
            break

        print("AI: ", end="", flush=True)

        for chunk, _ in chat_service.stream(
            query=user_input,
            session_id=session_id,
            persona=persona,
            language=language,
            use_rag=True,
            vectorstore=vectorstore,
        ):
            if hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)

        print("\n")


if __name__ == "__main__":
    main()
