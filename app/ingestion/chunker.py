from typing import List, Dict


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 500,
    overlap: int = 100,
) -> List[Dict]:
    """
    Split documents into overlapping chunks.

    Args:
        documents: Output of loader
        chunk_size: Size of each chunk (characters)
        overlap: Overlap between chunks (characters)

    Returns:
        List of chunked documents
    """
    chunks = []

    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]

        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
    "text": chunk_text,
    "metadata": {
        **metadata,
        "chunk_id": chunk_id,
        "text": chunk_text,
        "start": start,      
        "end": end           
    }
})



            chunk_id += 1
            start += chunk_size - overlap

    return chunks
