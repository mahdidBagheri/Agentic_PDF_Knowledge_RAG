import os
import shutil
from typing import List
from src.config import GEMINI_API_KEY
# Import your existing components
# (Adjust these import paths if your file structure is slightly different)
from src.llm.gemini_client import GeminiClient
from src.retrieval.retriever import Retriever
# You likely need a way to *add* to the vector store.
# Standard FAISS retrievers usually just read.
# We'll implement a helper here to handle the update logic.

import PyPDF2
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Define where the vector store lives
VECTORSTORE_PATH = "../vectorstore/faiss"


def ingest_pdf(file_path: str):
    """
    1. Reads PDF text
    2. Chunks the text
    3. Embeds and adds to FAISS index
    """
    print(f"📄 Starting ingestion for: {file_path}")

    # 1. Extract Text
    text = extract_text_from_pdf(file_path)
    if not text:
        raise ValueError("No text could be extracted from this PDF.")

    # 2. Chunk Text (Simple character splitting for now)
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    print(f"🧩 Split into {len(chunks)} chunks.")

    # 3. Create Documents for LangChain/FAISS
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": os.path.basename(file_path)}
        )
        for chunk in chunks
    ]

    # 4. Update (or Create) Vector Store
    update_vectorstore(documents, chunks)
    print("✅ Ingestion complete.")


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


from langchain_google_genai import GoogleGenerativeAIEmbeddings


def update_vectorstore(documents, chunks):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in config.py")

    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=chunks)

    embeddings = result.embeddings

    if os.path.exists(VECTORSTORE_PATH):
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(documents)
    else:
        vectorstore = FAISS.from_documents(documents, embeddings)

    vectorstore.save_local(VECTORSTORE_PATH)