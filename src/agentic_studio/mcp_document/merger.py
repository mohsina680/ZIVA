"""
Result merger for combining text from multiple extractors.
"""
from __future__ import annotations

from typing import List, Optional
import re

from .extractors.base import ExtractionResult


class ResultMerger:
    """
    Merges and deduplicates results from multiple extractors.

    Features:
    - Text deduplication
    - Confidence fusion
    - Quality-based filtering
    - Text fusion (preserve best parts from each)
    """

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize the result merger.

        Args:
            similarity_threshold: Minimum similarity to consider texts as duplicates (0-1)
        """
        self.similarity_threshold = similarity_threshold

    def merge(
        self,
        results: List[ExtractionResult],
        strategy: str = "best_confidence"
    ) -> ExtractionResult:
        """
        Merge multiple extraction results.

        Args:
            results: List of ExtractionResults to merge
            strategy: Merge strategy ("best_confidence", "concatenate", "fuse")

        Returns:
            Merged ExtractionResult
        """
        # Filter successful results
        successful = [r for r in results if not r.error and r.confidence > 0]

        if not successful:
            # Return the first result with error
            return results[0] if results else ExtractionResult(
                text="",
                confidence=0,
                error="No successful results to merge"
            )

        if strategy == "best_confidence":
            return self._merge_best_confidence(successful)
        elif strategy == "concatenate":
            return self._merge_concatenate(successful)
        elif strategy == "fuse":
            return self._merge_fuse(successful)
        else:
            return self._merge_best_confidence(successful)

    def _merge_best_confidence(self, results: List[ExtractionResult]) -> ExtractionResult:
        """Select the result with highest confidence."""
        best = max(results, key=lambda r: r.confidence)
        best.cache_hit = False
        return best

    def _merge_concatenate(self, results: List[ExtractionResult]) -> ExtractionResult:
        """Concatenate all results with extractor attribution."""
        combined_parts = []
        total_confidence = 0
        max_page_count = 0

        for result in sorted(results, key=lambda r: r.confidence, reverse=True):
            if result.text.strip():
                combined_parts.append(
                    f"[{result.extractor_name} - confidence: {result.confidence:.2f}]\n"
                    f"{result.text}"
                )
            total_confidence += result.confidence
            max_page_count = max(max_page_count, result.page_count)

        combined_text = "\n\n---\n\n".join(combined_parts)
        avg_confidence = total_confidence / len(results)

        return ExtractionResult(
            text=combined_text,
            confidence=avg_confidence,
            extractor_name="merged",
            page_count=max_page_count
        )

    def _merge_fuse(self, results: List[ExtractionResult]) -> ExtractionResult:
        """
        Intelligently fuse text from multiple results.

        Takes the longest/most complete text from the highest confidence extractor,
        then adds any unique content from lower confidence extractors.
        """
        # Sort by confidence
        sorted_results = sorted(results, key=lambda r: r.confidence, reverse=True)

        # Start with the best result
        best = sorted_results[0]
        fused_text = best.text
        fused_lines = set(best.text.split('\n'))

        # Try to add unique content from other extractors
        for result in sorted_results[1:]:
            if not result.text.strip():
                continue

            # Find unique lines from this result
            lines = result.text.split('\n')
            unique_lines = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if this line is substantially different
                if not self._is_similar_to_any(line, fused_lines):
                    unique_lines.append(line)
                    fused_lines.add(line)

            # Add unique content
            if unique_lines:
                fused_text += "\n\n[Additional from " + result.extractor_name + "]:\n"
                fused_text += "\n".join(unique_lines)

        # Calculate weighted confidence
        total_confidence = sum(r.confidence for r in results) / len(results)

        return ExtractionResult(
            text=fused_text,
            confidence=total_confidence,
            extractor_name="fused",
            page_count=best.page_count
        )

    def _is_similar_to_any(self, line: str, existing_lines: set) -> bool:
        """
        Check if a line is similar to any existing line.

        Uses simple word-based Jaccard similarity.
        """
        line_words = set(line.lower().split())

        for existing in existing_lines:
            existing_words = set(existing.lower().split())

            if not line_words or not existing_words:
                continue

            # Calculate Jaccard similarity
            intersection = len(line_words & existing_words)
            union = len(line_words | existing_words)

            if union > 0:
                similarity = intersection / union
                if similarity >= self.similarity_threshold:
                    return True

        return False

    def deduplicate(self, text: str) -> str:
        """
        Deduplicate text by removing duplicate lines and paragraphs.

        Args:
            text: Input text

        Returns:
            Deduplicated text
        """
        lines = text.split('\n')
        seen = set()
        result_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Normalize for comparison
            normalized = line.lower()

            if normalized not in seen:
                seen.add(normalized)
                result_lines.append(line)

        return '\n'.join(result_lines)


# Default merger instance
_default_merger: Optional[ResultMerger] = None


def get_default_merger() -> ResultMerger:
    """Get or create the default merger instance."""
    global _default_merger
    if _default_merger is None:
        _default_merger = ResultMerger()
    return _default_merger