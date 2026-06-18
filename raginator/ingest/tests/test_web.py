from unittest.mock import Mock, patch

from raginator.ingest import WebIngestor


def test_web_ingestor_strips_html_and_scripts():
    html = "<html><body><script>ignored()</script><p>Hello Web</p></body></html>"
    response = Mock(text=html, status_code=200)
    response.raise_for_status = Mock()

    with patch("raginator.ingest.web.requests.get", return_value=response) as mock_get:
        [document] = list(WebIngestor(["https://example.com"]).ingest())

    mock_get.assert_called_once_with("https://example.com", timeout=10.0)
    assert "Hello Web" in document.content
    assert "ignored" not in document.content
    assert document.metadata["url"] == "https://example.com"
    assert document.source_id == "https://example.com"
