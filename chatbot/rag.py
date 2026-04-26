"""
Simple TF-IDF based knowledge retrieval (RAG).

Loads .md and .txt files from a directory, splits into chunks,
and returns the most relevant chunks for a query.

For larger corpora, swap this for ChromaDB / FAISS + embeddings.
"""
import os
import re
from pathlib import Path
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks roughly chunk_size characters long."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


class KnowledgeBase:
    def __init__(self, docs_dir: str = "data"):
        self.docs_dir = Path(docs_dir)
        self.chunks: List[str] = []
        self.vectorizer = None
        self.matrix = None
        self._load()

    def _load(self) -> None:
        if not self.docs_dir.exists():
            return

        for path in self.docs_dir.rglob("*"):
            if path.suffix.lower() in (".md", ".txt") and path.is_file():
                try:
                    text = path.read_text(encoding="utf-8")
                    self.chunks.extend(_chunk_text(text))
                except Exception:
                    continue

        if self.chunks:
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.matrix = self.vectorizer.fit_transform(self.chunks)

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Return the top_k most relevant chunks for the query."""
        if not self.chunks or self.vectorizer is None:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix).flatten()
        # Filter out very low similarity chunks
        top_indices = sims.argsort()[::-1][:top_k]
        return [self.chunks[i] for i in top_indices if sims[i] > 0.05]
