# backend/rag.py

from backend.config import RAG_TOP_K


class RAGService:
    """
    A thin wrapper around a vectorstore that handles
    document retrieval for RAG.
    """

    def __init__(self, vectorstore=None):
        """
        vectorstore: any LangChain-compatible vectorstore (e.g. FAISS)
        """
        self.vectorstore = vectorstore

    def is_enabled(self) -> bool:
        """
        Check whether RAG is active.
        """
        return self.vectorstore is not None

    def retrieve(self, query: str) -> str:
        """
        Retrieve relevant document chunks for a query
        and return them as a single string.
        """
        if not self.vectorstore:
            return ""

        docs = self.vectorstore.similarity_search(query, k=RAG_TOP_K)

        return "\n\n".join(doc.page_content for doc in docs)
