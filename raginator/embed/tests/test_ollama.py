# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

from raginator.embed import OllamaEmbedder


def test_embed_texts_calls_local_ollama_server():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"embedding": [0.7, 0.8]}

    with patch("raginator.embed.ollama.requests.post", return_value=response) as mock_post:
        vectors = OllamaEmbedder().embed_texts(["hello"])

    assert vectors == [[0.7, 0.8]]
    args, kwargs = mock_post.call_args
    assert args[0] == "http://localhost:11434/api/embeddings"
    assert kwargs["json"] == {"model": "nomic-embed-text", "prompt": "hello"}


def test_custom_base_url_is_respected():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"embedding": [0.1]}

    with patch("raginator.embed.ollama.requests.post", return_value=response) as mock_post:
        OllamaEmbedder(base_url="http://example.com:11434/").embed_texts(["x"])

    args, _ = mock_post.call_args
    assert args[0] == "http://example.com:11434/api/embeddings"
