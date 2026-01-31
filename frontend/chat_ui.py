# frontend/chat_ui.py
from __future__ import annotations

import streamlit as st
from langchain_core.messages import AIMessage


def render_chat(chat: dict, chat_service) -> None:
    """
    Render chat history and handle streaming responses.
    Mutates chat['messages'].
    """
    # Display history
    for role, content in chat["messages"]:
        with st.chat_message(role):
            st.markdown(content)

    user_input = st.chat_input("Type your message...")

    if not user_input:
        return

    chat["messages"].append(("user", user_input))

    # Auto-title from first message
    if chat["title"] == "New chat":
        chat["title"] = user_input[:30] + ("…" if len(user_input) > 30 else "")

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        for chunk, _ in chat_service.stream(
            query=user_input,
            session_id=st.session_state.active_chat_id,
            persona=chat["persona"],
            language=chat["language"],
            use_rag=chat.get("use_rag", False),
            vectorstore=chat.get("vectorstore", None),
        ):
            if isinstance(chunk, AIMessage) and chunk.content:
                full_response += chunk.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)
        chat["messages"].append(("assistant", full_response))
