from unittest.mock import Mock, patch

import pytest
from ragfactory.core import StageError
from ragfactory.embed import HuggingFaceEmbedder


def test_embed_texts_calls_huggingface_api():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = [[0.1, 0.2], [0.3, 0.4]]

    with patch("ragfactory.embed.huggingface.requests.post", return_value=response) as mock_post:
        vectors = HuggingFaceEmbedder(api_key="test-key").embed_texts(["a", "b"])

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    assert kwargs["json"] == {"inputs": ["a", "b"]}


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGFACTORY_HUGGINGFACE_API_KEY", raising=False)

    with pytest.raises(StageError):
        HuggingFaceEmbedder().embed_texts(["a"])
