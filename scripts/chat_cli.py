# scripts/chat_cli.py
import os
import sys
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

# Export secrets as environment variables
os.environ["GOOGLE_API_KEY"] = secrets["GOOGLE_API_KEY"]
os.environ["LANGSMITH_API_KEY"] = secrets.get("LANGSMITH_API_KEY", "")

# --- Backend imports (after env vars are set) ---
from backend.model import get_chat_model
from backend.graph import build_graph
from backend.chat_service import ChatService


def main():
    # Step 1: Initialize model
    model = get_chat_model()

    
    # Step 2: Build LangGraph
    graph = build_graph(model)

    # Step 3: Create ChatService (no RAG)
    chat_service = ChatService(graph)

    session_id = "cli-session"

    print("\n🤖 Chatbot CLI")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye 👋")
            break

        print("AI: ", end="", flush=True)

        for chunk, _ in chat_service.stream(
            query=user_input,
            session_id=session_id,
            persona="Friendly Assistant",
            language="English",
        ):
            if hasattr(chunk, "content"):
                print(chunk.content, end="", flush=True)

        print("\n")


if __name__ == "__main__":
    main()
