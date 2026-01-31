import os
import sys
from pathlib import Path
import streamlit as st

# --- Fix import path ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# --- Load secrets ---
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# --- Backend imports ---
from backend.model import get_chat_model
from backend.graph import build_graph
from backend.chat_service import ChatService

# --- Frontend imports ---
from frontend.state import init_state
from frontend.sidebar import render_sidebar
from frontend.chat_ui import render_chat


def init_backend():
    if "chat_service" not in st.session_state:
        model = get_chat_model()
        graph = build_graph(model)
        st.session_state.chat_service = ChatService(graph)


def main():
    st.set_page_config(page_title="RAGFlow Chat", layout="wide")

    init_backend()
    init_state()

    # Centered title + subtitle
    st.markdown(
        """
        <style>
            .app-title {
                text-align: center;
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.2rem;
            }
            .app-subtitle {
                text-align: center;
                color: #9aa0a6;
                margin-bottom: 1.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-title">🧠 RAGFlow Chat</div>
        <div class="app-subtitle">
            Ask questions. Add documents. Get grounded answers.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Active chat dict
    chat = st.session_state.all_chats[st.session_state.active_chat_id]

    # Sidebar UI
    render_sidebar(chat)

    # Main chat UI
    render_chat(chat, st.session_state.chat_service)


if __name__ == "__main__":
    main()
