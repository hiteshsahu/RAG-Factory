# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

import pytest
from raginator.core import StageError
from raginator.embed import OpenAIEmbedder


def test_embed_texts_calls_openai_api():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"data": [{"embedding": [0.5, 0.6]}]}

    with patch("raginator.embed.openai.requests.post", return_value=response) as mock_post:
        vectors = OpenAIEmbedder(api_key="test-key").embed_texts(["hello"])

    assert vectors == [[0.5, 0.6]]
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"] == {"model": "text-embedding-3-small", "input": ["hello"]}


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGINATOR_OPENAI_API_KEY", raising=False)

    with pytest.raises(StageError):
        OpenAIEmbedder().embed_texts(["a"])
