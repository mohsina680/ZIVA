"""
Main document extraction orchestrator.
Combines all components for intelligent document extraction.
"""
from __future__ import annotations

from typing import Optional, List
from pathlib import Path

from .router import ExtractionRouter, RouterConfig, get_default_router
from .merger import ResultMerger, get_default_merger
from .cache import ExtractionCache, get_default_cache
from .extractors.base import ExtractionResult
from .analyzers.document_analyzer import DocumentAnalyzer, DocumentInfo


class DocumentExtractor:
    """
    Main document extraction orchestrator.

    Provides a simple interface for extracting text from documents
    using intelligent cascading extraction with caching.

    Usage:
        extractor = DocumentExtractor()
        result = extractor.extract("document.pdf")
        print(result.text)
        print(f"Confidence: {result.confidence}")
        print(f"Extractor: {result.extractor_name}")
    """

    def __init__(
        self,
        router: Optional[ExtractionRouter] = None,
        merger: Optional[ResultMerger] = None,
        cache: Optional[ExtractionCache] = None,
        use_cache: bool = True
    ):
        """
        Initialize the document extractor.

        Args:
            router: Extraction router (creates default if None)
            merger: Result merger (creates default if None)
            cache: Extraction cache (creates default if None)
            use_cache: Whether to use caching
        """
        self.router = router or get_default_router()
        self.merger = merger or get_default_merger()
        self.cache = cache or get_default_cache()
        self.use_cache = use_cache

    def extract(
        self,
        file_path: str,
        force_extractor: Optional[str] = None,
        min_confidence: float = 0.7,
        use_cache: Optional[bool] = None
    ) -> ExtractionResult:
        """
        Extract text from a document.

        Args:
            file_path: Path to PDF or image file
            force_extractor: Force a specific extractor ("tesseract", "docling", "easyocr", "surya")
            min_confidence: Minimum confidence threshold (0-1)
            use_cache: Override cache setting (uses instance default if None)

        Returns:
            ExtractionResult with extracted text and metadata
        """
        # Check cache first
        cache_enabled = use_cache if use_cache is not None else self.use_cache
        if cache_enabled:
            cached_result = self.cache.get(file_path)
            if cached_result and cached_result.is_successful():
                if cached_result.confidence >= min_confidence:
                    return cached_result

        # Analyze document
        doc_info = self.analyze(file_path)

        # Route and extract
        result = self.router.route(
            file_path,
            force_extractor=force_extractor,
            min_confidence=min_confidence
        )

        # Cache the result
        if cache_enabled and result.is_successful():
            self.cache.set(file_path, result)

        return result

    def extract_batch(
        self,
        file_paths: List[str],
        force_extractor: Optional[str] = None,
        min_confidence: float = 0.7,
        parallel: bool = False
    ) -> List[ExtractionResult]:
        """
        Extract text from multiple documents.

        Args:
            file_paths: List of file paths
            force_extractor: Force a specific extractor
            min_confidence: Minimum confidence threshold
            parallel: Whether to process in parallel (uses threading)

        Returns:
            List of ExtractionResults
        """
        if parallel:
            return self._extract_parallel(
                file_paths, force_extractor, min_confidence
            )
        else:
            return self._extract_sequential(
                file_paths, force_extractor, min_confidence
            )

    def _extract_sequential(
        self,
        file_paths: List[str],
        force_extractor: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> List[ExtractionResult]:
        """Extract documents sequentially."""
        results = []
        for path in file_paths:
            try:
                result = self.extract(
                    path,
                    force_extractor=force_extractor,
                    min_confidence=min_confidence
                )
                results.append(result)
            except Exception as e:
                results.append(ExtractionResult(
                    text="",
                    confidence=0,
                    error=str(e)
                ))
        return results

    def _extract_parallel(
        self,
        file_paths: List[str],
        force_extractor: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> List[ExtractionResult]:
        """Extract documents in parallel using threading."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    self.extract,
                    path,
                    force_extractor,
                    min_confidence
                ): path
                for path in file_paths
            }

            for future in as_completed(futures):
                path = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(ExtractionResult(
                        text="",
                        confidence=0,
                        error=str(e)
                    ))

        return results

    def analyze(self, file_path: str) -> DocumentInfo:
        """
        Analyze a document to determine its type and characteristics.

        Args:
            file_path: Path to document

        Returns:
            DocumentInfo with analysis results
        """
        analyzer = DocumentAnalyzer()
        return analyzer.analyze(file_path)

    def get_available_extractors(self) -> List[str]:
        """Get list of available extractors."""
        return self.router.get_available_extractors()

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return self.cache.get_stats()


# Convenience function
_default_extractor: Optional[DocumentExtractor] = None


def get_document_extractor() -> DocumentExtractor:
    """Get or create the default DocumentExtractor instance."""
    global _default_extractor
    if _default_extractor is None:
        _default_extractor = DocumentExtractor()
    return _default_extractor


def extract_document(
    file_path: str,
    force_extractor: Optional[str] = None,
    min_confidence: float = 0.7
) -> ExtractionResult:
    """
    Convenience function to extract text from a document.

    Args:
        file_path: Path to PDF or image file
        force_extractor: Force a specific extractor
        min_confidence: Minimum confidence threshold

    Returns:
        ExtractionResult with extracted text and metadata
    """
    extractor = get_document_extractor()
    return extractor.extract(
        file_path,
        force_extractor=force_extractor,
        min_confidence=min_confidence
    )