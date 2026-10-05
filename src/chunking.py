"""Step 2: split text into overlapping chunks."""
from __future__ import annotations

from dataclasses import dataclass

from .loaders import LoadedDocument


@dataclass
class Chunk:
    id: str
    text: str
    location: str


def split_text(text: str, size: int, overlap: int) -> list[str]:
    """Split on paragraph/sentence/word boundaries where possible."""
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []

    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            window = text[start:end]
            floor = int(size * 0.7)  # prefer a natural break in the last 30%
            for sep in ("\n\n", "\n", ". ", " "):
                cut = window.rfind(sep, floor)
                if cut != -1:
                    end = start + cut + len(sep)
                    break
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_document(doc: LoadedDocument, size: int, overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for seg in doc.segments:
        for piece in split_text(seg.text, size, overlap):
            chunks.append(Chunk(f"chunk_{len(chunks)}", piece, seg.location))
    return chunks
