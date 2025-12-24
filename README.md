# RAG Knowledge Assistant

A desktop-based **Retrieval-Augmented Generation (RAG)** application that allows users to upload documents, build a knowledge base, and ask questions grounded strictly in their own data.  
The system combines semantic search with large language models to provide accurate, document-backed answers.

![RAG Knowledge Assistant UI](./assets/ui.png)

---

## Features

- **Chat-based question answering**
- **Document ingestion** (PDF/text)
- **Semantic search with FAISS**
- **Google Gemini embeddings & LLM**
- **Context-grounded responses (RAG)**
- **Extensible pipeline** (reranking, confidence checks, agents)

---

## How It Works (RAG Pipeline)

1. **Ingestion**
   - Documents are loaded and chunked.
   - Each chunk is embedded using **Google Gemini embeddings**.
   - Embeddings are stored in a **FAISS vector index** on disk.

2. **Retrieval**
   - User questions are embedded using the **same embedding model**.
   - FAISS performs similarity search to retrieve relevant chunks.
   - Retrieved results are returned as `Document` objects.

3. **Context Processing**
   - `Document.page_content` text is extracted.
   - Contexts are passed as a list of strings to the prompt builder.

4. **Generation**
   - The final prompt combines:
     - User query
     - Retrieved document context
   - The Gemini LLM generates a grounded response.

---

## Interface Overview

The UI consists of two main tabs:

### 1. Chat
- Ask questions about your documents
- Responses are generated **only from your knowledge base**
- Clear chat-style interaction

### 2. Knowledge Base
- Upload and manage documents
- Build or refresh the vector store
- View ingestion status

The screenshot above shows:
- User query (left-aligned)
- AI response grounded in documents (green text)
- Input box for follow-up questions

## Setup Instructions

### 1. Clone the Repository
```
git clone https://github.com/your-username/rag-knowledge-assistant.git
cd rag-knowledge-assistant
```

### 2. Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Set your **Google Gemini API key**:

```
export GEMINI_API_KEY=your_api_key_here
```

or on Windows:
```
set GEMINI_API_KEY=your_api_key_here
```

---

## Running the Application

```
python src/ui/main_window.py
```

1. Upload documents to populate the knowledge base as PDF files.
2. Ask questions in the chat.
3. Receive grounded answers backed by your documents.

---

## Design Decisions

- **Single embedding model**  
  Both ingestion and retrieval use the same Gemini embedding model to avoid vector mismatch issues.

- **FAISS for local storage**  
  Fast, lightweight, and fully offline vector storage.

- **LangChain abstraction (selectively used)**  
  Provides standardized interfaces without locking the system into chains everywhere.

- **Stateless retrieval**  
  Vector store is loaded once and reused, improving performance.

---

## Future Improvements

- Cross-encoder reranking
- Confidence-based answer refusal
- Source citation display
- Streaming responses
- Multi-document collections
- Hybrid (BM25 + dense) retrieval

---

## License

MIT License

---

## Acknowledgements

- Google Gemini
- FAISS
- LangChain
- Sentence & embedding research community
