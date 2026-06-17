from __future__ import annotations

import math
import re
from collections import Counter

from ragfactory.core import Chunk, RetrievedChunk, Retriever

_TOKEN_RE = re.compile(r"\w+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class SparseRetriever(Retriever):
    """Keyword-based retrieval via BM25 (The Find-Inator, sparse mode).

    Maintains its own corpus, separate from any vector store -- Pipeline.index()
    calls index() automatically for every batch of chunks it produces.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._chunks: list[Chunk] = []
        self._term_frequencies: list[Counter[str]] = []
        self._doc_frequency: Counter[str] = Counter()
        self._doc_lengths: list[int] = []

    def index(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            tokens = _tokenize(chunk.content)
            term_frequency = Counter(tokens)
            self._chunks.append(chunk)
            self._term_frequencies.append(term_frequency)
            self._doc_lengths.append(len(tokens))
            for term in term_frequency:
                self._doc_frequency[term] += 1

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        if not self._chunks:
            return []

        query_terms = _tokenize(query)
        num_docs = len(self._chunks)
        avg_doc_length = sum(self._doc_lengths) / num_docs

        scores = [
            self._score(query_terms, index, avg_doc_length) for index in range(num_docs)
        ]
        ranked = sorted(range(num_docs), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            RetrievedChunk(chunk=self._chunks[i], score=scores[i], rank=rank)
            for rank, i in enumerate(ranked)
        ]

    def _score(self, query_terms: list[str], doc_index: int, avg_doc_length: float) -> float:
        term_frequency = self._term_frequencies[doc_index]
        doc_length = self._doc_lengths[doc_index]
        num_docs = len(self._chunks)

        score = 0.0
        for term in query_terms:
            frequency = term_frequency.get(term, 0)
            if frequency == 0:
                continue
            document_frequency = self._doc_frequency[term]
            idf = math.log((num_docs - document_frequency + 0.5) / (document_frequency + 0.5) + 1)
            denominator = frequency + self._k1 * (
                1 - self._b + self._b * doc_length / avg_doc_length
            )
            score += idf * (frequency * (self._k1 + 1)) / denominator
        return score
