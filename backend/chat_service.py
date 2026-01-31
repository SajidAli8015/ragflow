# backend/chat_service.py

from langchain_core.messages import HumanMessage, AIMessage
from google.api_core.exceptions import ResourceExhausted

from backend.rag import RAGService


class ChatService:
    def __init__(self, graph):
        self.graph = graph

    def stream(
        self,
        query: str,
        session_id: str,
        persona: str,
        language: str,
        use_rag: bool = False,
        vectorstore=None,
    ):
        # Get document context (if any)
        retrieved_context = ""
        if use_rag and vectorstore is not None:
            retrieved_context = RAGService(vectorstore).retrieve(query)

        input_data = {
            "messages": [HumanMessage(content=query)],
            "persona": persona,
            "language": language,
            "retrieved_context": retrieved_context,
        }

        try:
            for chunk, metadata in self.graph.stream(
                input_data,
                {"configurable": {"thread_id": session_id}},
                stream_mode="messages",
            ):
                yield chunk, metadata

        except ResourceExhausted:
            # Simple, friendly message — no crash
            yield (
                AIMessage(content="⚠️ API quota exceeded. Please wait a bit and try again."),
                None,
            )
