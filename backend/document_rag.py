# backend/document_rag.py
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import BytesIO, StringIO

import pandas as pd
import docx
from PyPDF2 import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from backend.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME


SUPPORTED_EXTENSIONS = {"pdf", "txt", "docx", "csv"}


@dataclass(frozen=True)
class BuiltIndex:
    vectorstore: FAISS
    file_hash: str
    filename: str


def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = _ext(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: .{ext}")

    bio = BytesIO(file_bytes)

    if ext == "pdf":
        reader = PdfReader(bio)
        return "\n".join([(p.extract_text() or "") for p in reader.pages])

    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    if ext == "docx":
        document = docx.Document(bio)
        return "\n".join([p.text for p in document.paragraphs])

    if ext == "csv":
        text = file_bytes.decode("utf-8", errors="ignore")
        df = pd.read_csv(StringIO(text))
        return df.to_string(index=False)

    raise ValueError(f"Unsupported file type: .{ext}")


def build_vectorstore_from_upload(file_bytes: bytes, filename: str) -> BuiltIndex:
    file_hash = compute_file_hash(file_bytes)
    raw_text = extract_text(file_bytes, filename)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(raw_text)

    if not chunks:
        raise ValueError("No text could be extracted from this file.")

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

    return BuiltIndex(vectorstore=vectorstore, file_hash=file_hash, filename=filename)
