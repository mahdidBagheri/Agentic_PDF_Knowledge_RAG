from ingestion.pdf_loader import load_pdfs
from ingestion.chunker import chunk_documents

if "__main__" == __name__:

    docs = load_pdfs("../data/raw_pdfs")
    chunks = chunk_documents(docs, chunk_size=500, overlap=50)

    print(f"Total chunks: {len(chunks)}")

    for c in chunks[:3]:
        print("\n---")
        print(c["chunk_id"])
        print(c["text"][:400])