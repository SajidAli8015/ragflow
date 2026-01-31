# frontend/sidebar.py
from __future__ import annotations

import streamlit as st
from frontend.state import apply_rename, create_new_chat, safe_index


def render_sidebar(chat: dict) -> None:
    """
    Render sidebar UI and mutate the active chat dict in-place.
    """
    with st.sidebar:
        st.header("Chats")

        # New chat
        if st.button("➕ New chat"):
            create_new_chat()
            st.rerun()

        st.divider()

        # Chat list + rename
        for cid, c in st.session_state.all_chats.items():
            is_active = cid == st.session_state.active_chat_id

            col1, col2 = st.columns([0.85, 0.15])

            with col1:
                if st.button(
                    c["title"],
                    key=f"open_{cid}",
                    use_container_width=True,
                ):
                    st.session_state.active_chat_id = cid
                    st.rerun()

            with col2:
                if is_active:
                    if st.button("✏️", key=f"edit_{cid}"):
                        c["renaming"] = True
                        st.rerun()

            if is_active and c["renaming"]:
                st.text_input(
                    "Rename chat",
                    value=c["title"],
                    key=f"title_input_{cid}",
                    on_change=apply_rename,
                    args=(cid,),
                )

        # ---------- RAG section ----------
        st.divider()
        st.subheader("📄 Document (RAG)")

        uploaded = st.file_uploader(
            "Upload a file",
            type=["pdf", "txt", "docx", "csv"],
            key=f"uploader_{st.session_state.active_chat_id}",
        )

        if uploaded is not None:
            from backend.document_rag import build_vectorstore_from_upload

            file_bytes = uploaded.getvalue()
            filename = uploaded.name

            try:
                built = build_vectorstore_from_upload(file_bytes, filename)

                if chat.get("last_file_hash") != built.file_hash:
                    chat["vectorstore"] = built.vectorstore
                    chat["last_file_hash"] = built.file_hash
                    chat["use_rag"] = True
                    st.success(f"✅ Embedded: {built.filename}. RAG enabled for this chat.")
                else:
                    st.info("ℹ️ Same file already loaded for this chat. Skipping embedding.")

            except Exception as e:
                st.error(f"Upload failed: {e}")

        chat["use_rag"] = st.checkbox(
            "Use document context (RAG)",
            value=chat.get("use_rag", False),
        )

        # ---------- Persona & Language ----------
        st.divider()
        st.subheader("🎛️ Chat settings")

        persona_options = ["Friendly Assistant", "Formal Expert", "Tech Support"]
        language_options = ["English", "Urdu", "Arabic"]

        chat["persona"] = st.selectbox(
            "Persona",
            persona_options,
            index=safe_index(
                persona_options,
                chat.get("persona", "Friendly Assistant"),
                "Friendly Assistant",
            ),
            key=f"persona_{st.session_state.active_chat_id}",
        )

        chat["language"] = st.selectbox(
            "Language",
            language_options,
            index=safe_index(
                language_options,
                chat.get("language", "English"),
                "English",
            ),
            key=f"language_{st.session_state.active_chat_id}",
        )

        # ---------- Actions ----------
        st.divider()
        st.subheader("🧹 Actions")

        if st.button("🔄 Reset messages", use_container_width=True):
            chat["messages"] = []
            st.rerun()

        conversation_text = "\n\n".join(
            [f"{'You' if role == 'user' else 'AI'}: {content}" for role, content in chat["messages"]]
        )

        st.download_button(
            label="⬇️ Download chat (.txt)",
            data=conversation_text.encode("utf-8"),
            file_name=f"{(chat.get('title') or 'chat').replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=(len(chat["messages"]) == 0),
        )
