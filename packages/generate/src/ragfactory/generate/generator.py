from __future__ import annotations

from ragfactory.core import Generator


class TemplateGenerator(Generator):
    """Concatenates retrieved context into a templated answer (The Answer-Inator).

    No LLM call is made; swap in a real LLM-backed Generator to actually answer.
    """

    def generate(self, query: str, context: list[str]) -> str:
        if not context:
            return f"No context found for: {query}"
        joined = "\n---\n".join(context)
        return f"Q: {query}\n\nContext:\n{joined}"
