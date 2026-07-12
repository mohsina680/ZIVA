"""
Document type analyzer for intelligent extractor selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import os


class DocumentType(Enum):
    """Types of documents."""
    NATIVE_PDF = "native_pdf"        # Searchable PDF with embedded text
    SCANNED_PDF = "scanned_pdf"     # Scanned/image-based PDF
    IMAGE_SCAN = "image_scan"        # Scanned image
    IMAGE_PHOTO = "image_photo"      # Photo/image (not a scan)
    UNKNOWN = "unknown"


@dataclass
class DocumentInfo:
    """Information about a document."""
    path: str
    document_type: DocumentType
    file_size_bytes: int
    page_count: int = 1
    is_searchable: bool = False
    estimated_quality: float = 0.5  # 0-1, higher = better quality
    detected_language: str = "unknown"
    raw_text_length: int = 0


class DocumentAnalyzer:
    """
    Analyzes documents to determine type and optimal extraction strategy.
    """

    def __init__(self):
        self._file_type_cache: dict[str, DocumentType] = {}

    def analyze(self, file_path: str) -> DocumentInfo:
        """
        Analyze a document and return information about it.

        Args:
            file_path: Path to the document

        Returns:
            DocumentInfo with metadata about the document
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        # Detect document type
        doc_type = self._detect_document_type(file_path)

        # Get file info
        file_size = path.stat().st_size
        page_count = self._estimate_page_count(file_path)
        is_searchable = self._is_searchable_pdf(file_path) if doc_type in (
            DocumentType.NATIVE_PDF, DocumentType.SCANNED_PDF
        ) else False

        # Estimate quality based on file characteristics
        quality = self._estimate_quality(file_path, doc_type, is_searchable)

        return DocumentInfo(
            path=file_path,
            document_type=doc_type,
            file_size_bytes=file_size,
            page_count=page_count,
            is_searchable=is_searchable,
            estimated_quality=quality
        )

    def _detect_document_type(self, file_path: str) -> DocumentType:
        """
        Detect the type of document based on file extension and content.
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == '.pdf':
            # For PDFs, we need to check if it's searchable
            if self._has_embedded_text(file_path):
                return DocumentType.NATIVE_PDF
            return DocumentType.SCANNED_PDF

        elif ext in {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}:
            # For images, detect if it looks like a scan or photo
            if self._looks_like_scan(file_path):
                return DocumentType.IMAGE_SCAN
            return DocumentType.IMAGE_PHOTO

        return DocumentType.UNKNOWN

    def _has_embedded_text(self, file_path: str) -> bool:
        """
        Check if PDF has embedded text (not just images).
        Uses PyPDF2 or pypdf to count text characters.
        """
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            total_text = 0
            for page in reader.pages:
                text = page.extract_text() or ""
                total_text += len(text.strip())

            # If we found significant text, it's a native PDF
            return total_text > 100
        except Exception:
            return False

    def _is_searchable_pdf(self, file_path: str) -> bool:
        """Alias for _has_embedded_text."""
        return self._has_embedded_text(file_path)

    def _looks_like_scan(self, file_path: str) -> bool:
        """
        Heuristic to detect if an image looks like a scan vs a photo.

        Scans typically have:
        - White/light backgrounds
        - Sharp edges
        - Text-like patterns
        - Less photographic content

        This is a simple heuristic - actual scan detection would use ML.
        """
        try:
            from PIL import Image
            import numpy as np

            img = Image.open(file_path)

            # Convert to grayscale
            if img.mode != 'L':
                img = img.convert('L')

            arr = np.array(img)

            # Calculate contrast - scans typically have high contrast
            contrast = arr.std() / (arr.mean() + 1)

            # Check for white background (scan characteristic)
            bright_pixels = (arr > 240).sum()
            bright_ratio = bright_pixels / arr.size

            # High contrast + white background = likely scan
            if contrast > 0.4 and bright_ratio > 0.3:
                return True

            return False
        except Exception:
            # If PIL not available, assume it's a scan
            return True

    def _estimate_page_count(self, file_path: str) -> int:
        """Estimate the number of pages in a document."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == '.pdf':
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                return len(reader.pages)
            except Exception:
                return 1

        return 1  # Images are single-page by default

    def _estimate_quality(
        self,
        file_path: str,
        doc_type: DocumentType,
        is_searchable: bool
    ) -> float:
        """
        Estimate document quality (0-1).
        Higher = higher likely extraction quality.
        """
        path = Path(file_path)
        size_mb = path.stat().st_size / (1024 * 1024)

        base_quality = 0.5

        # Native PDFs with text are high quality
        if doc_type == DocumentType.NATIVE_PDF and is_searchable:
            base_quality = 0.95

        # Scanned PDFs might work well with OCR
        elif doc_type == DocumentType.SCANNED_PDF:
            base_quality = 0.6 if size_mb < 5 else 0.7

        # Image scans
        elif doc_type == DocumentType.IMAGE_SCAN:
            # Higher resolution = better quality
            try:
                from PIL import Image
                img = Image.open(file_path)
                area = img.width * img.height
                if area > 4000000:  # > 4MP
                    base_quality = 0.75
                elif area > 1000000:  # > 1MP
                    base_quality = 0.65
            except Exception:
                pass

        return min(base_quality, 1.0)

    def get_recommended_extractors(self, doc_info: DocumentInfo) -> list[str]:
        """
        Get ordered list of recommended extractors for a document.

        Args:
            doc_info: Document information from analysis

        Returns:
            List of extractor names in order of recommendation
        """
        doc_type = doc_info.document_type

        # Define extraction order by document type
        extraction_map = {
            DocumentType.NATIVE_PDF: ["docling", "tesseract", "easyocr", "surya"],
            DocumentType.SCANNED_PDF: ["tesseract", "easyocr", "surya", "docling"],
            DocumentType.IMAGE_SCAN: ["tesseract", "easyocr", "surya"],
            DocumentType.IMAGE_PHOTO: ["easyocr", "tesseract", "surya"],
            DocumentType.UNKNOWN: ["tesseract", "easyocr", "docling", "surya"],
        }

        return extraction_map.get(doc_type, ["tesseract", "easyocr", "surya"])