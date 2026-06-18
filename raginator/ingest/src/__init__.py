from .github import GitHubIngestor
from .ingestor import TextFileIngestor
from .pdf import PDFIngestor
from .s3 import S3Ingestor
from .web import WebIngestor

__all__ = ["GitHubIngestor", "PDFIngestor", "S3Ingestor", "TextFileIngestor", "WebIngestor"]
