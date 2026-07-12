"""
Base extractor class for all document extraction backends.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import time


@dataclass
class ExtractionResult:
    """Result from a document extraction operation."""

    text: str = ""
    confidence: float = 0.0
    extractor_name: str = "unknown"
    page_count: int = 0
    language: str = "unknown"
    extraction_time_ms: int = 0
    cache_hit: bool = False
    error: Optional[str] = None
    pages_results: list[str] = field(default_factory=list)

    def is_successful(self) -> bool:
        """Check if extraction succeeded."""
        return self.error is None and self.confidence > 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "extractor_used": self.extractor_name,
            "page_count": self.page_count,
            "language": self.language,
            "extraction_time_ms": self.extraction_time_ms,
            "cache_hit": self.cache_hit,
            "error": self.error,
            "successful": self.is_successful()
        }


class BaseExtractor(ABC):
    """
    Abstract base class for document extractors.

    All extractors must implement:
    - is_available(): Check if the extractor is installed/configured
    - extract(): Perform the actual extraction
    """

    name: str = "base"
    description: str = "Base extractor"

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this extractor is available and ready to use.

        Returns:
            True if the extractor can be used, False otherwise.
        """
        pass

    @abstractmethod
    def extract(self, file_path: str, **kwargs) -> ExtractionResult:
        """
        Extract text from a document.

        Args:
            file_path: Path to the document (PDF or image)
            **kwargs: Additional extractor-specific options

        Returns:
            ExtractionResult with extracted text and metadata
        """
        pass

    def extract_page(self, file_path: str, page: int = 0, **kwargs) -> ExtractionResult:
        """
        Extract text from a specific page of a document.

        Default implementation calls extract() and returns result for that page.
        Extractors can override this for more efficient per-page processing.

        Args:
            file_path: Path to the document
            page: Page number (0-indexed)
            **kwargs: Additional options

        Returns:
            ExtractionResult for the specific page
        """
        return self.extract(file_path, **kwargs)

    def _measure_time(func):
        """Decorator to measure extraction time."""
        def wrapper(self, file_path: str, **kwargs):
            start = time.time()
            result = func(self, file_path, **kwargs)
            result.extraction_time_ms = int((time.time() - start) * 1000)
            return result
        return wrapper

    def _create_result(
        self,
        text: str,
        confidence: float = 0.8,
        page_count: int = 1,
        error: Optional[str] = None
    ) -> ExtractionResult:
        """Helper to create an ExtractionResult."""
        return ExtractionResult(
            text=text,
            confidence=confidence,
            extractor_name=self.name,
            page_count=page_count,
            error=error
        )

    def get_priority(self) -> int:
        """
        Get the priority of this extractor (lower = try first).

        Returns:
            Priority number (1 = highest priority, 10 = lowest)
        """
        return 5


class ImageExtractor(ABC):
    """
    Mixin for extractors that primarily work on images.
    """

    @staticmethod
    def is_image_file(path: str) -> bool:
        """Check if path is an image file."""
        image_exts = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}
        return Path(path).suffix.lower() in image_exts


class PDFExtractor(ABC):
    """
    Mixin for extractors that can handle PDFs.
    """

    @staticmethod
    def is_pdf_file(path: str) -> bool:
        """Check if path is a PDF file."""
        return Path(path).suffix.lower() == '.pdf'