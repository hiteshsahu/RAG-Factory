from unittest.mock import Mock, patch

import pytest
from ragfactory.core import StageError
from ragfactory.embed import MistralEmbedder


def test_embed_texts_calls_mistral_api():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"data": [{"embedding": [0.1, 0.2]}, {"embedding": [0.3, 0.4]}]}

    with patch("ragfactory.embed.mistral.requests.post", return_value=response) as mock_post:
        vectors = MistralEmbedder(api_key="test-key").embed_texts(["a", "b"])

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"] == {"model": "mistral-embed", "input": ["a", "b"]}


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGFACTORY_MISTRAL_API_KEY", raising=False)

    with pytest.raises(StageError):
        MistralEmbedder().embed_texts(["a"])
