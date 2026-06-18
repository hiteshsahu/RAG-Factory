from __future__ import annotations

from raginator.core import GeneratedAnswer, StageError

# Snapshot pricing, USD per 1M tokens (blended; doesn't distinguish input vs.
# output pricing). Verify against each provider's current pricing page before
# relying on this for real budgeting -- these numbers go stale fast.
PRICING_PER_MILLION_TOKENS: dict[str, float] = {
    "mistral-small-latest": 0.20,
    "mistral-large-latest": 2.00,
    "mistral-embed": 0.10,
    "gpt-4o-mini": 0.15,
    "gpt-4o": 2.50,
    "text-embedding-3-small": 0.02,
}


def cost_per_query(
    answer: GeneratedAnswer, model: str, pricing: dict[str, float] | None = None
) -> float:
    """Estimated USD cost of one generated answer, from its token usage."""
    price_per_million = (pricing or PRICING_PER_MILLION_TOKENS).get(model)
    if price_per_million is None:
        raise StageError("evaluate", f"No pricing data for model '{model}'")
    return (answer.tokens_used / 1_000_000) * price_per_million


def cost_per_million_tokens(model: str, pricing: dict[str, float] | None = None) -> float:
    """Looks up the configured $/1M token rate for a model."""
    price_per_million = (pricing or PRICING_PER_MILLION_TOKENS).get(model)
    if price_per_million is None:
        raise StageError("evaluate", f"No pricing data for model '{model}'")
    return price_per_million
