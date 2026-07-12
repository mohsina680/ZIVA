"""
ZIVA Document Extractor MCP Tool
================================
A 100% free/open-source document extraction tool using cascading OCR.

Extractors:
- Tesseract (system OCR)
- Docling (native PDF parsing)
- EasyOCR (pure Python, CPU-based)
- Surya OCR (Microsoft's open-source OCR)
"""

from .extractor import DocumentExtractor, extract_document, get_document_extractor
from .merger import ExtractionResult

__all__ = ["DocumentExtractor", "ExtractionResult", "extract_document", "get_document_extractor"]
__version__ = "0.1.0"