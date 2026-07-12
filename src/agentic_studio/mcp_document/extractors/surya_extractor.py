"""
Surya OCR extractor - Microsoft's open-source OCR with layout detection.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, List

from .base import BaseExtractor, ExtractionResult


class SuryaExtractor(BaseExtractor):
    """
    Surya OCR extractor.

    Surya is Microsoft's open-source OCR library that provides:
    - Layout detection (text, tables, images)
    - Document OCR
    - High accuracy
    - Multiple language support

    Install: pip install surya-ocr
    Note: Requires torch and transformers
    """

    name = "surya"
    description = "Surya OCR (Microsoft's open-source, layout-aware)"

    def __init__(self, languages: Optional[List[str]] = None):
        """
        Initialize Surya OCR extractor.

        Args:
            languages: List of language codes (default: ['en'])
        """
        self._languages = languages or ["en"]
        self._ocr_model = None
        self._layout_model = None
        self._init_error: Optional[str] = None

    def _get_models(self):
        """Lazy initialization of Surya models."""
        if self._ocr_model is None and self._init_error is None:
            try:
                from surya.ocr import run_ocr
                from surya.layout import run_layout
                self._ocr_model = run_ocr
                self._layout_model = run_layout
            except ImportError as e:
                self._init_error = f"Surya not installed: {e}"
            except Exception as e:
                self._init_error = str(e)
        return self._ocr_model, self._layout_model

    def is_available(self) -> bool:
        """Check if Surya OCR is available."""
        try:
            ocr, layout = self._get_models()
            return ocr is not None
        except Exception:
            return False

    def extract(self, file_path: str, **kwargs) -> ExtractionResult:
        """
        Extract text from a document using Surya OCR.

        Args:
            file_path: Path to PDF or image file
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

        try:
            return self._extract_file(file_path, **kwargs)
        except Exception as e:
            return self._create_result(
                text="",
                confidence=0,
                error=str(e)
            )

    def _extract_file(self, file_path: str, **kwargs) -> ExtractionResult:
        """Extract text from file using Surya OCR."""
        from PIL import Image
        from pathlib import Path

        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == '.pdf':
            return self._extract_pdf(file_path, **kwargs)
        else:
            return self._extract_image(file_path, **kwargs)

    def _extract_image(self, file_path: str, **kwargs) -> ExtractionResult:
        """Extract text from a single image using Surya."""
        from PIL import Image
        import numpy as np

        ocr_func, layout_func = self._get_models()
        if ocr_func is None:
            return self._create_result(
                text="",
                confidence=0,
                error=f"Surya not available: {self._init_error}"
            )

        try:
            # Load image
            if isinstance(file_path, str):
                image = Image.open(file_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image_array = np.array(image)
            else:
                image_array = file_path

            # Run OCR
            # Surya expects image files or IDs
            predictions = ocr_func(
                images=[image_array],
                languages=self._languages
            )

            # Process results
            if not predictions or len(predictions) == 0:
                return self._create_result(
                    text="",
                    confidence=0,
                    error="No text found in image"
                )

            pred = predictions[0]
            all_text = []
            confidences = []

            # Extract text from text lines
            for line in pred.text_lines:
                text = line.text
                if text.strip():
                    all_text.append(text)
                    # Surya provides confidence per text line
                    if hasattr(line, 'confidence') and line.confidence:
                        confidences.append(line.confidence)

            combined_text = "\n".join(all_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.7

            return self._create_result(
                text=combined_text,
                confidence=avg_confidence,
                page_count=1
            )
        except Exception as e:
            return self._create_result(text="", confidence=0, error=str(e))

    def _extract_pdf(self, file_path: str, **kwargs) -> ExtractionResult:
        """Extract text from PDF using Surya OCR on each page."""
        from pdf2image import convert_from_path

        ocr_func, _ = self._get_models()
        if ocr_func is None:
            return self._create_result(
                text="",
                confidence=0,
                error=f"Surya not available: {self._init_error}"
            )

        try:
            # Convert PDF pages to images
            images = convert_from_path(file_path, dpi=200)
            page_images = [img.convert('RGB') for img in images]

            # Process in batches
            all_results = []
            batch_size = kwargs.get('batch_size', 5)

            for i in range(0, len(page_images), batch_size):
                batch = page_images[i:i + batch_size]
                batch_arrays = [np.array(img) for img in batch]

                predictions = ocr_func(
                    images=batch_arrays,
                    languages=self._languages
                )
                all_results.extend(predictions)

            # Process results
            all_text = []
            confidences = []

            for page_num, pred in enumerate(all_results, 1):
                page_lines = []
                for line in pred.text_lines:
                    text = line.text.strip()
                    if text:
                        page_lines.append(text)
                        if hasattr(line, 'confidence') and line.confidence:
                            confidences.append(line.confidence)

                page_text = "\n".join(page_lines)
                all_text.append(f"--- Page {page_num} ---\n{page_text}")

            combined_text = "\n\n".join(all_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.7

            return self._create_result(
                text=combined_text,
                confidence=avg_confidence,
                page_count=len(images)
            )
        except Exception as e:
            return self._create_result(text="", confidence=0, error=str(e))

    def get_priority(self) -> int:
        """
        Surya is accurate but may require more resources.
        Use as fallback.
        """
        return 4


# Singleton instance
_surya_instance: Optional[SuryaExtractor] = None


def get_surya_extractor() -> Optional[SuryaExtractor]:
    """Get or create singleton Surya extractor."""
    global _surya_instance
    if _surya_instance is None:
        extractor = SuryaExtractor()
        if extractor.is_available():
            _surya_instance = extractor
    return _surya_instance