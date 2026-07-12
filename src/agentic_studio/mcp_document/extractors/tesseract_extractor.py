"""
Tesseract OCR extractor.
Uses system-installed Tesseract for fast OCR.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, Union

from .base import BaseExtractor, ExtractionResult


class TesseractExtractor(BaseExtractor):
    """
    Tesseract OCR extractor.

    Requires Tesseract to be installed on the system.
    On Windows: Install from https://github.com/UB-Mannheim/tesseract/wiki
    On Linux: sudo apt-get install tesseract-ocr
    On macOS: brew install tesseract

    Also requires:
    - pytesseract (Python bindings)
    - pdf2image (for PDF processing)
    - poppler-utils (for pdf2image on Linux)
    """

    name = "tesseract"
    description = "Tesseract OCR (system-installed, fast)"

    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = "eng"):
        """
        Initialize Tesseract extractor.

        Args:
            tesseract_cmd: Path to tesseract executable (auto-detected if None)
            lang: Language code for Tesseract (default: eng)
        """
        self._tesseract_cmd = tesseract_cmd or "tesseract"
        self._lang = lang

    def is_available(self) -> bool:
        """Check if Tesseract is installed and working."""
        try:
            result = subprocess.run(
                [self._tesseract_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def extract(self, file_path: str, **kwargs) -> ExtractionResult:
        """
        Extract text from a document using Tesseract OCR.

        Args:
            file_path: Path to PDF or image file
            **kwargs: Additional options (lang, dpi, etc.)

        Returns:
            ExtractionResult with extracted text
        """
        lang = kwargs.get("lang", self._lang)
        dpi = kwargs.get("dpi", 300)

        path = Path(file_path)
        if not path.exists():
            return self._create_result(
                text="",
                confidence=0,
                error=f"File not found: {file_path}"
            )

        ext = path.suffix.lower()

        try:
            if ext == '.pdf':
                return self._extract_from_pdf(file_path, lang, dpi)
            else:
                return self._extract_from_image(file_path, lang, dpi)
        except Exception as e:
            return self._create_result(
                text="",
                confidence=0,
                error=str(e)
            )

    def _extract_from_image(self, file_path: str, lang: str, dpi: int) -> ExtractionResult:
        """Extract text from an image using Tesseract."""
        import pytesseract
        from PIL import Image

        try:
            img = Image.open(file_path)

            # Configure Tesseract
            config = f"--oem 3 --psm 1 -l {lang}"

            # Extract text
            text = pytesseract.image_to_string(img, config=config)

            # Get confidence
            data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data["conf"] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0

            return self._create_result(
                text=text.strip(),
                confidence=avg_confidence,
                page_count=1
            )
        except Exception as e:
            return self._create_result(text="", confidence=0, error=str(e))

    def _extract_from_pdf(self, file_path: str, lang: str, dpi: int) -> ExtractionResult:
        """Extract text from PDF by converting pages to images first."""
        from pdf2image import convert_from_path

        try:
            # Convert PDF pages to images
            images = convert_from_path(file_path, dpi=dpi)

            all_text = []
            confidences = []

            for page_num, img in enumerate(images, 1):
                try:
                    import pytesseract

                    config = f"--oem 3 --psm 1 -l {lang}"
                    page_text = pytesseract.image_to_string(img, config=config)

                    # Get confidence for this page
                    data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)
                    page_conf = [int(c) for c in data["conf"] if int(c) > 0]
                    if page_conf:
                        confidences.append(sum(page_conf) / len(page_conf) / 100)

                    all_text.append(f"--- Page {page_num} ---\n{page_text.strip()}")
                except Exception as e:
                    all_text.append(f"--- Page {page_num} ---\n[OCR Error: {str(e)}]")

            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

            return self._create_result(
                text="\n\n".join(all_text),
                confidence=avg_confidence,
                page_count=len(images)
            )
        except Exception as e:
            return self._create_result(text="", confidence=0, error=str(e))

    def get_priority(self) -> int:
        """Tesseract is fast and usually reliable - high priority."""
        return 1


# Singleton instance
_tesseract_instance: Optional[TesseractExtractor] = None


def get_tesseract_extractor() -> Optional[TesseractExtractor]:
    """Get or create singleton Tesseract extractor."""
    global _tesseract_instance
    if _tesseract_instance is None:
        extractor = TesseractExtractor()
        if extractor.is_available():
            _tesseract_instance = extractor
    return _tesseract_instance