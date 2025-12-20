import os
from typing import List, Dict
import pdfplumber


def load_pdfs(pdf_dir: str) -> List[Dict]:
    """
    Load all PDFs from a directory and extract text page by page.

    Returns a list of documents with metadata:
    [
        {
            "text": "...",
            "source": "HR_Policy_Handbook.pdf",
            "page": 1
        }
    ]
    """

    documents = []

    if not os.path.exists(pdf_dir):
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        raise ValueError(f"No PDF files found in {pdf_dir}")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()

                    if text is None:
                        continue

                    text = text.strip()

                    if not text:
                        continue

                    documents.append(
                        {
                            "text": text,
                            "source": pdf_file,
                            "page": page_number,
                        }
                    )

        except Exception as e:
            print(f"❌ Failed to process {pdf_file}: {e}")

    return documents

if __name__ == "__main__":
    docs = load_pdfs("../../data/raw_pdfs")
    print(f"Loaded {len(docs)} pages")

    for doc in docs[:2]:
        print("\n---")
        print(f"Source: {doc['source']}, Page: {doc['page']}")
        print(doc["text"][:500])