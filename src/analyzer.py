"""Step 5: RAG + the document analysis features."""
from __future__ import annotations

import json

from . import prompts
from .config import MAX_CONTEXT_CHARS, TOP_K
from .llm import GroqLLM
from .vector_store import VectorStore


class DocumentAnalyzer:
    def __init__(self, store: VectorStore, llm: GroqLLM, doc_name: str):
        self.store = store
        self.llm = llm
        self.doc_name = doc_name

    # ---------- Ask questions (full RAG) ----------
    def ask(self, question: str, history: list[dict] | None = None) -> tuple[str, list[dict]]:
        hits = self.store.search(question, TOP_K)
        context = "\n\n".join(
            f"[{i}] ({h['location']})\n{h['text']}" for i, h in enumerate(hits, 1)
        )
        convo = ""
        if history:
            recent = history[-6:]
            convo = "Previous conversation:\n" + "\n".join(
                f"{m['role'].title()}: {m['content']}" for m in recent
            ) + "\n\n"
        user = f"{convo}Document excerpts:\n{context}\n\nQuestion: {question}"
        return self.llm.ask(prompts.QA, user, max_tokens=900), hits

    # ---------- Whole-document features ----------
    def _context(self) -> str:
        return self.store.sample_context(MAX_CONTEXT_CHARS)

    def summarize(self, style: str = "concise paragraph") -> str:
        chunks = self.store.chunks
        total = sum(len(c.text) for c in chunks)
        if total <= MAX_CONTEXT_CHARS:
            text = self._context()
        else:
            # map-reduce: summarise groups of chunks, then combine
            groups, buf, size = [], [], 0
            for c in chunks:
                buf.append(c.text)
                size += len(c.text)
                if size > 6000:
                    groups.append("\n\n".join(buf))
                    buf, size = [], 0
            if buf:
                groups.append("\n\n".join(buf))
            groups = groups[:8]  # cap API calls
            partials = [self.llm.ask(prompts.SUMMARY_CHUNK, g, max_tokens=300) for g in groups]
            text = "\n\n".join(f"Part {i}: {p}" for i, p in enumerate(partials, 1))
        return self.llm.ask(
            prompts.SUMMARY_FINAL, f"Style: {style}\n\nDocument:\n{text}", max_tokens=700
        )

    def keywords(self) -> list[str]:
        data = self.llm.ask_json(prompts.KEYWORDS, self._context(), max_tokens=400)
        return [str(k) for k in data.get("keywords", [])]

    def important_points(self) -> str:
        return self.llm.ask(prompts.POINTS, self._context(), max_tokens=800)

    def structured_data(self) -> dict:
        return self.llm.ask_json(prompts.STRUCTURED, self._context(), max_tokens=1500)

    def quiz(self, n: int = 5) -> list[dict]:
        data = self.llm.ask_json(
            prompts.QUIZ, f"Number of questions: {n}\n\nDocument:\n{self._context()}",
            temperature=0.4, max_tokens=2000,
        )
        valid = []
        for q in data.get("questions", []):
            opts = q.get("options", [])
            idx = q.get("answer_index")
            if len(opts) == 4 and isinstance(idx, int) and 0 <= idx < 4 and q.get("question"):
                valid.append(q)
        return valid

    def report(self, summary: str, keywords: list[str], points: str, structured: dict) -> str:
        user = (
            f"Document name: {self.doc_name}\n\n"
            f"Summary:\n{summary}\n\nKeywords: {', '.join(keywords)}\n\n"
            f"Important points:\n{points}\n\n"
            f"Structured data:\n{json.dumps(structured, indent=2)}\n\n"
            f"Document excerpt:\n{self._context()[:8000]}"
        )
        return self.llm.ask(prompts.REPORT, user, max_tokens=1500)
