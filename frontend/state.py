# frontend/state.py
from __future__ import annotations

import uuid
import streamlit as st


def new_chat_state() -> dict:
    return {
        "title": "New chat",
        "messages": [],
        "persona": "Friendly Assistant",
        "language": "English",
        "use_rag": False,
        "vectorstore": None,
        "last_file_hash": None,
        "renaming": False,
    }


def init_state() -> None:
    if "all_chats" not in st.session_state:
        st.session_state.all_chats = {}

    if "active_chat_id" not in st.session_state:
        chat_id = str(uuid.uuid4())
        st.session_state.active_chat_id = chat_id
        st.session_state.all_chats[chat_id] = new_chat_state()


def safe_index(options, value, default) -> int:
    """Return a safe index into options."""
    if value in options:
        return options.index(value)
    if default in options:
        return options.index(default)
    return 0


def apply_rename(chat_id: str) -> None:
    chat = st.session_state.all_chats[chat_id]
    new_title = st.session_state.get(f"title_input_{chat_id}", "").strip()
    if new_title:
        chat["title"] = new_title
    chat["renaming"] = False


def create_new_chat() -> None:
    chat_id = str(uuid.uuid4())
    st.session_state.all_chats[chat_id] = new_chat_state()
    st.session_state.active_chat_id = chat_id
