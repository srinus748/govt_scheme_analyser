# utils/text_chunker.py

def chunk_text_simple(text: str, max_chunk_size: int = 2500, overlap: int = 200) -> list[str]:
    """
    Splits a large string into smaller chunks with a specified overlap.
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks
