# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from .docx import DocxIngestor
from .github import GitHubIngestor
from .ingestor import TextFileIngestor
from .pdf import PDFIngestor
from .s3 import S3Ingestor
from .web import WebIngestor

__all__ = ["DocxIngestor", "GitHubIngestor", "PDFIngestor", "S3Ingestor", "TextFileIngestor", "WebIngestor"]
