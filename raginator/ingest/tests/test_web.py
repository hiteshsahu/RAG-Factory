# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

from raginator.ingest.web import USER_AGENT, WebIngestor


def test_web_ingestor_strips_html_and_scripts():
    html = "<html><body><script>ignored()</script><p>Hello Web</p></body></html>"
    response = Mock(text=html, status_code=200)
    response.raise_for_status = Mock()

    with patch("raginator.ingest.web.requests.get", return_value=response) as mock_get:
        [document] = list(WebIngestor(["https://example.com"]).ingest())

    mock_get.assert_called_once_with("https://example.com", timeout=10.0, headers={"User-Agent": USER_AGENT})
    assert "Hello Web" in document.content
    assert "ignored" not in document.content
    assert document.metadata["url"] == "https://example.com"
    assert document.source_id == "https://example.com"


def test_web_ingestor_sends_a_descriptive_user_agent():
    # Wikipedia (among others) 403s the default "python-requests/X.Y" UA --
    # this is the regression that broke it.
    response = Mock(text="<p>content</p>", status_code=200)
    response.raise_for_status = Mock()

    with patch("raginator.ingest.web.requests.get", return_value=response) as mock_get:
        list(WebIngestor(["https://en.wikipedia.org/wiki/Reflection_(physics)"]).ingest())

    assert mock_get.call_args.kwargs["headers"]["User-Agent"] == USER_AGENT
    assert "python-requests" not in USER_AGENT
