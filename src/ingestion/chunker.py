import re
from typing import List, Dict


def _clean_text(text: str) -> str:
    """
    Light text cleaning only.
    Preserves original meaning.
    """
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove space before punctuation
    text = re.sub(r"\s([?.!,])", r"\1", text)

    return text.strip()


def _split_into_sentences(text: str) -> List[str]:
    """
    Simple sentence splitter using regex.
    Good enough for structured documents.
    """
    sentence_endings = re.compile(r"(?<=[.!?])\s+")
    return sentence_endings.split(text)


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[Dict]:
    """
    Chunk documents into overlapping chunks.

    Parameters:
    - documents: list of dicts with 'text', 'source', 'page'
    - chunk_size: approximate word count (not tokens)
    - overlap: number of words to overlap between chunks

    Returns:
    [
        {
            "chunk_id": "...",
            "text": "...",
            "source": "...",
            "page": ...
        }
    ]
    """

    chunks = []

    for doc in documents:
        source = doc["source"]
        page = doc["page"]

        clean_text = _clean_text(doc["text"])

        if not clean_text:
            continue

        sentences = _split_into_sentences(clean_text)

        current_chunk = []
        current_length = 0
        chunk_index = 0

        for sentence in sentences:
            words = sentence.split()
            sentence_length = len(words)

            # If a single sentence is too large, hard cut
            if sentence_length > chunk_size:
                for i in range(0, sentence_length, chunk_size):
                    split_words = words[i:i + chunk_size]
                    chunk_text = " ".join(split_words)

                    chunks.append(
                        {
                            "chunk_id": f"{source}_p{page}_c{chunk_index}",
                            "text": chunk_text,
                            "source": source,
                            "page": page,
                        }
                    )
                    chunk_index += 1
                continue

            # Start new chunk if needed
            if current_length + sentence_length > chunk_size:
                chunk_text = " ".join(current_chunk)

                chunks.append(
                    {
                        "chunk_id": f"{source}_p{page}_c{chunk_index}",
                        "text": chunk_text,
                        "source": source,
                        "page": page,
                    }
                )

                chunk_index += 1

                # Handle overlap
                if overlap > 0:
                    overlap_words = chunk_text.split()[-overlap:]
                    current_chunk = overlap_words.copy()
                    current_length = len(current_chunk)
                else:
                    current_chunk = []
                    current_length = 0

            # Add sentence
            current_chunk.extend(words)
            current_length += sentence_length

        # Flush final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                {
                    "chunk_id": f"{source}_p{page}_c{chunk_index}",
                    "text": chunk_text,
                    "source": source,
                    "page": page,
                }
            )

    return chunks

