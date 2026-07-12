"""
Smart document extraction router.
Routes documents to appropriate extractors based on type and confidence.
"""
from __future__ import annotations

from typing import Optional, List, Dict, Type
from dataclasses import dataclass

from .analyzers.document_analyzer import DocumentAnalyzer, DocumentInfo, DocumentType
from .extractors.base import BaseExtractor, ExtractionResult
from .extractors.tesseract_extractor import TesseractExtractor
from .extractors.docling_extractor import DoclingExtractor
from .extractors.easyocr_extractor import EasyOCRExtractor
from .extractors.surya_extractor import SuryaExtractor


@dataclass
class RouterConfig:
    """Configuration for the extraction router."""

    # Confidence thresholds
    min_confidence: float = 0.7      # Minimum acceptable confidence
    high_confidence: float = 0.85     # Consider extraction successful

    # Whether to try multiple extractors and merge results
    multi_extractor_mode: bool = False

    # Extractor availability cache refresh interval (seconds)
    availability_cache_ttl: int = 300


class ExtractionRouter:
    """
    Smart router that selects the best extractor for a document.

    The router:
    1. Analyzes the document to determine its type
    2. Selects extractors in order of priority
    3. Tries extractors until confidence threshold is met
    4. Optionally merges results from multiple extractors
    """

    def __init__(self, config: Optional[RouterConfig] = None):
        """
        Initialize the extraction router.

        Args:
            config: Router configuration (uses defaults if None)
        """
        self.config = config or RouterConfig()
        self.analyzer = DocumentAnalyzer()

        # Initialize and register extractors
        self._extractors: Dict[str, BaseExtractor] = {}
        self._extractor_availability: Dict[str, bool] = {}
        self._register_extractors()

    def _register_extractors(self) -> None:
        """Register all available extractors."""
        # Try to create each extractor
        extractors_to_register = [
            ("tesseract", TesseractExtractor),
            ("docling", DoclingExtractor),
            ("easyocr", EasyOCRExtractor),
            ("surya", SuryaExtractor),
        ]

        for name, extractor_class in extractors_to_register:
            try:
                extractor = extractor_class()
                if extractor.is_available():
                    self._extractors[name] = extractor
                    self._extractor_availability[name] = True
                else:
                    self._extractor_availability[name] = False
            except Exception as e:
                self._extractor_availability[name] = False

    def get_available_extractors(self) -> List[str]:
        """Get list of available extractor names."""
        return [name for name, available in self._extractor_availability.items()
                if available]

    def get_extractor(self, name: str) -> Optional[BaseExtractor]:
        """Get extractor by name."""
        return self._extractors.get(name)

    def select_extractors(
        self,
        doc_info: DocumentInfo,
        force_extractor: Optional[str] = None
    ) -> List[BaseExtractor]:
        """
        Select extractors for a document in priority order.

        Args:
            doc_info: Document information
            force_extractor: Force a specific extractor (bypass smart selection)

        Returns:
            Ordered list of extractors to try
        """
        if force_extractor:
            extractor = self._extractors.get(force_extractor)
            if extractor:
                return [extractor]
            else:
                available = self.get_available_extractors()
                if available:
                    return [self._extractors[available[0]]]
                return []

        # Get recommendations based on document type
        recommended_order = self.analyzer.get_recommended_extractors(doc_info)

        # Filter to only available extractors
        selected = []
        for name in recommended_order:
            if name in self._extractors and name in self._extractor_availability:
                if self._extractor_availability[name]:
                    selected.append(self._extractors[name])

        return selected

    def route(
        self,
        file_path: str,
        force_extractor: Optional[str] = None,
        min_confidence: Optional[float] = None
    ) -> ExtractionResult:
        """
        Route document to appropriate extractors with cascading.

        Args:
            file_path: Path to document
            force_extractor: Force a specific extractor
            min_confidence: Override minimum confidence threshold

        Returns:
            ExtractionResult from the first successful extractor
        """
        if min_confidence is None:
            min_confidence = self.config.min_confidence

        try:
            # Analyze document
            doc_info = self.analyzer.analyze(file_path)
        except Exception as e:
            # Return error if we can't even analyze
            return ExtractionResult(
                text="",
                confidence=0,
                error=f"Document analysis failed: {e}"
            )

        # Select extractors
        extractors = self.select_extractors(doc_info, force_extractor)

        if not extractors:
            return ExtractionResult(
                text="",
                confidence=0,
                error="No extractors available"
            )

        # Try each extractor in order
        last_result = None
        for extractor in extractors:
            try:
                result = extractor.extract(file_path)

                if result.error:
                    # Try next extractor
                    last_result = result
                    continue

                # Check if we're satisfied with this result
                if result.confidence >= min_confidence:
                    return result
                elif result.confidence >= self.config.high_confidence:
                    # Very high confidence - accept even if below our threshold
                    return result

                # Save result but continue trying
                last_result = result

            except Exception as e:
                # Try next extractor
                last_result = ExtractionResult(
                    text="",
                    confidence=0,
                    extractor_name=extractor.name,
                    error=str(e)
                )
                continue

        # Return last result if all failed or were below threshold
        if last_result:
            return last_result

        return ExtractionResult(
            text="",
            confidence=0,
            error="All extractors failed"
        )

    def route_multi(
        self,
        file_path: str,
        force_extractor: Optional[str] = None
    ) -> List[ExtractionResult]:
        """
        Route document to multiple extractors and return all results.

        Used when multi_extractor_mode is enabled or for comparison.

        Args:
            file_path: Path to document
            force_extractor: Force a specific extractor

        Returns:
            List of ExtractionResults from all extractors
        """
        try:
            doc_info = self.analyzer.analyze(file_path)
        except Exception as e:
            return [ExtractionResult(
                text="",
                confidence=0,
                error=f"Document analysis failed: {e}"
            )]

        extractors = self.select_extractors(doc_info, force_extractor)

        results = []
        for extractor in extractors:
            try:
                result = extractor.extract(file_path)
                results.append(result)
            except Exception as e:
                results.append(ExtractionResult(
                    text="",
                    confidence=0,
                    extractor_name=extractor.name,
                    error=str(e)
                ))

        return results


# Default router instance
_default_router: Optional[ExtractionRouter] = None


def get_default_router() -> ExtractionRouter:
    """Get or create the default router instance."""
    global _default_router
    if _default_router is None:
        _default_router = ExtractionRouter()
    return _default_router