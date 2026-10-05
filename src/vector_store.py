"""Steps 3-4: embeddings + vector database (ChromaDB, in memory)."""
from __future__ import annotations

import uuid

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .chunking import Chunk


class Embedder:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        ).tolist()


class VectorStore:
    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.client = chromadb.EphemeralClient(
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        self.collection = self.client.create_collection(
            name=f"doc_{uuid.uuid4().hex[:12]}",
            metadata={"hnsw:space": "cosine"},
        )
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        batch = 64
        for i in range(0, len(chunks), batch):
            part = chunks[i:i + batch]
            self.collection.add(
                ids=[c.id for c in part],
                documents=[c.text for c in part],
                embeddings=self.embedder.embed([c.text for c in part]),
                metadatas=[{"location": c.location} for c in part],
            )

    def search(self, query: str, k: int) -> list[dict]:
        k = max(1, min(k, len(self.chunks)))
        res = self.collection.query(
            query_embeddings=self.embedder.embed([query]), n_results=k
        )
        return [
            {"text": doc, "location": meta["location"], "score": 1 - dist}
            for doc, meta, dist in zip(
                res["documents"][0], res["metadatas"][0], res["distances"][0]
            )
        ]

    def sample_context(self, max_chars: int) -> str:
        """Whole document if it fits, otherwise evenly spaced chunks, in order."""
        full = "\n\n".join(c.text for c in self.chunks)
        if len(full) <= max_chars:
            return full
        avg = max(1, len(full) // len(self.chunks))
        want = max(1, max_chars // avg)
        step = max(1, len(self.chunks) // want)
        picked, total = [], 0
        for c in self.chunks[::step]:
            if total + len(c.text) > max_chars:
                break
            picked.append(c.text)
            total += len(c.text)
        return "\n\n".join(picked)

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection.name)
        except Exception:
            pass
