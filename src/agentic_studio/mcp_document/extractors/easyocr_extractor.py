"""
EasyOCR extractor - pure Python OCR, CPU-based, no GPU required.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional, List

from .base import BaseExtractor, ExtractionResult


class EasyOCRExtractor(BaseExtractor):
    """
    EasyOCR-based extractor.

    EasyOCR is:
    - Pure Python (no system dependencies)
    - Works on CPU (GPU not required)
    - Supports many languages
    - MIT licensed

    Install: pip install easyocr
    """

    name = "easyocr"
    description = "EasyOCR (pure Python, CPU-based, MIT license)"

    def __init__(self, languages: Optional[List[str]] = None):
        """
        Initialize EasyOCR extractor.

        Args:
            languages: List of language codes (default: ['en'])
        """
        self._languages = languages or ['en']
        self._reader = None
        self._init_error: Optional[str] = None

    def _get_reader(self):
        """Lazy initialization of EasyOCR reader."""
        if self._reader is None and self._init_error is None:
            try:
                import easyocr
                # EasyOCR works on CPU by default when no GPU
                self._reader = easyocr.Reader(
                    self._languages,
                    gpu=False,  # Force CPU mode
                    verbose=False
                )
            except Exception as e:
                self._init_error = str(e)
                return None
        return self._reader

    def is_available(self) -> bool:
        """Check if EasyOCR is available."""
        try:
            reader = self._get_reader()
            return reader is not None
        except Exception:
            return False

    def extract(self, file_path: str, **kwargs) -> ExtractionResult:
        """
        Extract text from a document using EasyOCR.

        Args:
            file_path: Path to PDF or image file
            **kwargs: Additional options (batch_size, etc.)

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

        try:
            return self._extract_file(file_path, **kwargs)
        except Exception as e:
            return self._create_result(
                text="",
                confidence=0,
                error=str(e)
            )

    def _extract_file(self, file_path: str, **kwargs) -> ExtractionResult:
        """Extract text from file using EasyOCR."""
        import easyocr
        from PIL import Image
        import numpy as np

        reader = self._get_reader()
        if reader is None:
            return self._create_result(
                text="",
                confidence=0,
                error=f"EasyOCR not available: {self._init_error}"
            )

        path = Path(file_path)
        ext = path.suffix.lower()

        start_time = time.time()

        if ext == '.pdf':
            return self._extract_pdf(file_path, reader)
        else:
            return self._extract_image(file_path, reader)

    def _extract_image(self, file_path: str, reader) -> ExtractionResult:
        """Extract text from a single image."""
        from PIL import Image
        import numpy as np

        try:
            # Read image
            img = Image.open(file_path)
            img_array = np.array(img)

            # Perform OCR
            results = reader.readtext(img_array)

            # Process results
            all_text = []
            confidences = []

            for bbox, text, confidence in results:
                if text.strip():
                    all_text.append(text.strip())
                    confidences.append(confidence)

            combined_text = " ".join(all_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return self._create_result(
                text=combined_text,
                confidence=avg_confidence,
                page_count=1
            )
        except Exception as e:
            return self._create_result(text="", confidence=0, error=str(e))

    def _extract_pdf(self, file_path: str, reader) -> ExtractionResult:
        """Extract text from PDF by processing each page as an image."""
        from pdf2image import convert_from_path
        from PIL import Image
        import numpy as np

        try:
            # Convert PDF pages to images
            images = convert_from_path(file_path, dpi=200)

            all_text = []
            confidences = []
            page_results = []

            for page_num, img in enumerate(images, 1):
                try:
                    img_array = np.array(img)
                    results = reader.readtext(img_array)

                    page_lines = []
                    page_conf = []
                    for bbox, text, confidence in results:
                        if text.strip():
                            page_lines.append(text.strip())
                            page_conf.append(confidence)

                    page_text = " ".join(page_lines)
                    page_results.append(f"--- Page {page_num} ---\n{page_text}")

                    if page_conf:
                        confidences.append(sum(page_conf) / len(page_conf))

                    all_text.append(page_text)
                except Exception as e:
                    page_results.append(f"--- Page {page_num} ---\n[OCR Error: {str(e)}]")

            combined_text = "\n\n".join(page_results)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

            return self._create_result(
                text=combined_text,
                confidence=avg_confidence,
                page_count=len(images)
            )
        except Exception as e:
            return self._create_result(text="", confidence=0, error=str(e))

    def get_priority(self) -> int:
        """
        EasyOCR is CPU-based and slower but more accessible.
        Medium priority - try Tesseract first.
        """
        return 3


# Singleton instance
_easyocr_instance: Optional[EasyOCRExtractor] = None


def get_easyocr_extractor() -> Optional[EasyOCRExtractor]:
    """Get or create singleton EasyOCR extractor."""
    global _easyocr_instance
    if _easyocr_instance is None:
        extractor = EasyOCRExtractor()
        if extractor.is_available():
            _easyocr_instance = extractor
    return _easyocr_instance