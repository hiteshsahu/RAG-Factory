from unittest.mock import Mock, patch

from raginator.core import Chunk, RetrievedChunk
from raginator.generate import OllamaGenerator


def _context(text: str) -> RetrievedChunk:
    chunk = Chunk(content=text, metadata={}, chunk_id="c", doc_id="d")
    return RetrievedChunk(chunk=chunk, score=1.0, rank=0)


def test_generate_calls_local_ollama_chat_endpoint():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {
        "message": {"content": "Doofenshmirtz built it."},
        "eval_count": 10,
        "prompt_eval_count": 30,
    }

    with patch("raginator.generate.ollama.requests.post", return_value=response) as mock_post:
        answer = OllamaGenerator().generate(
            "Who built it?", [_context("Doofenshmirtz built the Raginator.")]
        )

    assert answer.answer == "Doofenshmirtz built it."
    assert answer.tokens_used == 40
    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:11434/api/chat"
    assert kwargs["json"]["model"] == "llama3.2"
    assert kwargs["json"]["stream"] is False


def test_custom_base_url_is_respected():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"message": {"content": "hi"}}

    with patch("raginator.generate.ollama.requests.post", return_value=response) as mock_post:
        OllamaGenerator(base_url="http://example.com:11434/").generate("q", [])

    args, _ = mock_post.call_args
    assert args[0] == "http://example.com:11434/api/chat"
