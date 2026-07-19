# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

import base64
from unittest.mock import Mock, patch

from raginator.ingest import GitHubIngestor


def test_github_ingestor_fetches_only_markdown_files():
    tree_response = Mock(status_code=200)
    tree_response.raise_for_status = Mock()
    tree_response.json.return_value = {
        "tree": [
            {"path": "README.md", "type": "blob", "url": "https://api.github.com/blob/1"},
            {"path": "main.py", "type": "blob", "url": "https://api.github.com/blob/2"},
            {"path": "docs", "type": "tree", "url": "https://api.github.com/tree/1"},
        ]
    }

    blob_response = Mock(status_code=200)
    blob_response.raise_for_status = Mock()
    blob_response.json.return_value = {
        "content": base64.b64encode(b"# Hello Docs").decode("ascii")
    }

    with patch(
        "raginator.ingest.github.requests.get", side_effect=[tree_response, blob_response]
    ) as mock_get:
        [document] = list(GitHubIngestor("owner", "repo", token="x").ingest())

    assert mock_get.call_count == 2
    assert document.content == "# Hello Docs"
    assert document.metadata["path"] == "README.md"
    assert document.source_id == "owner/repo/README.md"


def test_github_ingestor_uses_settings_token_by_default(monkeypatch):
    monkeypatch.setenv("RAGINATOR_GITHUB_TOKEN", "from-env")

    ingestor = GitHubIngestor("owner", "repo")

    assert ingestor._headers()["Authorization"] == "Bearer from-env"
