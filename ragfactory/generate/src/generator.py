from __future__ import annotations

from ragfactory.core import GeneratedAnswer, Generator, RetrievedChunk


class TemplateGenerator(Generator):
    """Concatenates retrieved context into a templated answer (The Answer-Inator).

    No LLM call is made; swap in a real LLM-backed Generator to actually answer.
    """

    def generate(self, query: str, context: list[RetrievedChunk]) -> GeneratedAnswer:
        if not context:
            return GeneratedAnswer(answer=f"No context found for: {query}", sources=[])
        joined = "\n---\n".join(retrieved.chunk.content for retrieved in context)
        answer = f"Q: {query}\n\nContext:\n{joined}"
        return GeneratedAnswer(answer=answer, sources=context)
