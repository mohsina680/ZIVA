"""
Docling extractor for PDF document parsing.
Docling is an open-source document understanding library.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .base import BaseExtractor, ExtractionResult


class DoclingExtractor(BaseExtractor):
    """
    Docling-based document extractor.

    Docling is great for:
    - Native/searchable PDFs
    - Structured document parsing
    - Table extraction
    - Layout preservation

    Install: pip install docling
    """

    name = "docling"
    description = "Docling (open-source PDF parser, great for structured docs)"

    def __init__(self):
        """Initialize Docling extractor."""
        self._initialized = False

    def is_available(self) -> bool:
        """Check if Docling is available."""
        try:
            import docling
            self._initialized = True
            return True
        except ImportError:
            return False

    def extract(self, file_path: str, **kwargs) -> ExtractionResult:
        """
        Extract text from a document using Docling.

        Args:
            file_path: Path to PDF file
            **kwargs: Additional options

        Returns:
            ExtractionResult with extracted text
        """
        path = Path(file_path)
        if not path.exists():
            return self._create_result(
                text="",
                confidence=0,
                error=f"File not found: {file_path}"
            )

        if path.suffix.lower() != '.pdf':
            return self._create_result(
                text="",
                confidence=0,
                error="Docling only supports PDF files"
            )

        try:
            return self._extract_pdf(file_path, **kwargs)
        except Exception as e:
            return self._create_result(
                text="",
                confidence=0,
                error=str(e)
            )

    def _extract_pdf(self, file_path: str, **kwargs) -> ExtractionResult:
        """Extract text from PDF using Docling."""
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.backend.pypdf_backend import PyPdfDocumentBackend

        try:
            # Configure converter
            converter = DocumentConverter(
                valid_format=[InputFormat.PDF],
                backend=PyPdfDocumentBackend
            )

            # Convert document
            result = converter.convert(file_path)

            # Get markdown output (preserves structure)
            markdown_text = result.document.export_to_markdown()

            # Get page count
            page_count = len(result.document.pages) if hasattr(result.document, 'pages') else 1

            # Docling confidence is typically high for native PDFs
            confidence = 0.9 if len(markdown_text.strip()) > 100 else 0.5

            return self._create_result(
                text=markdown_text,
                confidence=confidence,
                page_count=page_count
            )
        except Exception as e:
            # Try fallback with simple pypdf extraction
            return self._extract_fallback_pdf(file_path)

    def _extract_fallback_pdf(self, file_path: str) -> ExtractionResult:
        """Fallback extraction using pypdf if Docling fails."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            page_count = len(reader.pages)

            all_text = []
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                all_text.append(f"--- Page {i} ---\n{text.strip()}")

            combined_text = "\n\n".join(all_text)
            confidence = 0.85 if len(combined_text.strip()) > 100 else 0.4

            return self._create_result(
                text=combined_text,
                confidence=confidence,
                page_count=page_count
            )
        except Exception as e:
            return self._create_result(
                text="",
                confidence=0,
                error=f"Docling and fallback extraction failed: {e}"
            )

    def get_priority(self) -> int:
        """Docling is great for native PDFs - high priority."""
        return 2


# Singleton instance
_docling_instance: Optional[DoclingExtractor] = None


def get_docling_extractor() -> Optional[DoclingExtractor]:
    """Get or create singleton Docling extractor."""
    global _docling_instance
    if _docling_instance is None:
        extractor = DoclingExtractor()
        if extractor.is_available():
            _docling_instance = extractor
    return _docling_instance