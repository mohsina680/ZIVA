"""
Tests for MCP Document Extraction module.
"""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from agentic_studio.mcp_document.extractors.base import BaseExtractor, ExtractionResult
from agentic_studio.mcp_document.analyzers.document_analyzer import DocumentAnalyzer, DocumentType, DocumentInfo
from agentic_studio.mcp_document.router import ExtractionRouter, RouterConfig
from agentic_studio.mcp_document.merger import ResultMerger
from agentic_studio.mcp_document.cache import ExtractionCache, get_default_cache


class TestExtractors:
    """Test that extractors are properly configured."""

    def test_base_extractor_interface(self):
        """Test that the base extractor interface is correct."""
        # Check ExtractionResult dataclass
        result = ExtractionResult(
            text="test",
            confidence=0.8,
            extractor_name="test",
            page_count=1
        )
        assert result.text == "test"
        assert result.confidence == 0.8
        assert result.is_successful()
        assert result.error is None

    def test_extraction_result_error(self):
        """Test ExtractionResult with error."""
        result = ExtractionResult(
            text="",
            confidence=0,
            error="Test error"
        )
        assert not result.is_successful()
        assert result.error == "Test error"

    def test_extraction_result_to_dict(self):
        """Test ExtractionResult serialization."""
        result = ExtractionResult(
            text="Hello World",
            confidence=0.85,
            extractor_name="test",
            page_count=2
        )

        d = result.to_dict()
        assert d["text"] == "Hello World"
        assert d["confidence"] == 0.85
        assert d["extractor_used"] == "test"
        assert d["page_count"] == 2
        assert d["successful"] is True


class TestDocumentAnalyzer:
    """Test document type detection."""

    def test_document_type_enum(self):
        """Test DocumentType enum values."""
        assert DocumentType.NATIVE_PDF.value == "native_pdf"
        assert DocumentType.SCANNED_PDF.value == "scanned_pdf"
        assert DocumentType.IMAGE_SCAN.value == "image_scan"
        assert DocumentType.IMAGE_PHOTO.value == "image_photo"

    def test_document_info(self):
        """Test DocumentInfo dataclass."""
        info = DocumentInfo(
            path="/test/path.pdf",
            document_type=DocumentType.NATIVE_PDF,
            file_size_bytes=1024,
            page_count=5,
            is_searchable=True,
            estimated_quality=0.95
        )

        assert info.document_type == DocumentType.NATIVE_PDF
        assert info.page_count == 5
        assert info.is_searchable


class TestRouter:
    """Test extraction router."""

    def test_router_config(self):
        """Test router configuration."""
        config = RouterConfig(
            min_confidence=0.8,
            high_confidence=0.9
        )
        assert config.min_confidence == 0.8
        assert config.high_confidence == 0.9

    def test_default_router_config(self):
        """Test default router configuration."""
        config = RouterConfig()
        assert config.min_confidence == 0.7
        assert config.high_confidence == 0.85


class TestMerger:
    """Test result merger."""

    def test_best_confidence_merger(self):
        """Test merge with best confidence strategy."""
        merger = ResultMerger()

        results = [
            ExtractionResult(text="Test 1", confidence=0.5, extractor_name="a"),
            ExtractionResult(text="Test 2", confidence=0.8, extractor_name="b"),
            ExtractionResult(text="Test 3", confidence=0.6, extractor_name="c"),
        ]

        merged = merger.merge(results, strategy="best_confidence")
        assert merged.confidence == 0.8
        assert merged.text == "Test 2"

    def test_concatenate_merger(self):
        """Test merge with concatenation strategy."""
        merger = ResultMerger()

        results = [
            ExtractionResult(text="Test 1", confidence=0.5, extractor_name="a"),
            ExtractionResult(text="Test 2", confidence=0.8, extractor_name="b"),
        ]

        merged = merger.merge(results, strategy="concatenate")
        assert "Test 1" in merged.text
        assert "Test 2" in merged.text
        assert merged.extractor_name == "merged"

    def test_deduplication(self):
        """Test text deduplication."""
        merger = ResultMerger()

        text = """
        Line 1
        Line 2
        Line 1
        Line 3
        Line 2
        """

        deduplicated = merger.deduplicate(text)
        lines = deduplicated.strip().split('\n')

        # Should have only 3 unique lines
        assert len(lines) == 3


class TestCache:
    """Test extraction cache."""

    def test_cache_init(self, tmp_path):
        """Test cache initialization."""
        cache = ExtractionCache(cache_dir=str(tmp_path / "cache"))
        assert cache.cache_dir.exists()
        assert cache._index == {}

    def test_cache_stats(self, tmp_path):
        """Test cache statistics."""
        cache = ExtractionCache(cache_dir=str(tmp_path / "cache"))
        stats = cache.get_stats()

        assert "entries" in stats
        assert "cache_dir" in stats
        assert stats["entries"] == 0


class TestExtractionResult:
    """Test ExtractionResult class."""

    def test_extractors_import_all(self):
        """Test that all extractor classes can be imported."""
        from agentic_studio.mcp_document.extractors.tesseract_extractor import TesseractExtractor
        from agentic_studio.mcp_document.extractors.docling_extractor import DoclingExtractor
        from agentic_studio.mcp_document.extractors.easyocr_extractor import EasyOCRExtractor
        from agentic_studio.mcp_document.extractors.surya_extractor import SuryaExtractor

        assert TesseractExtractor is not None
        assert DoclingExtractor is not None
        assert EasyOCRExtractor is not None
        assert SuryaExtractor is not None

    def test_cache_module_import(self):
        """Test that cache module can be imported."""
        assert ExtractionCache is not None
        assert get_default_cache is not None

    def test_tools_module_import(self):
        """Test that tools module can be imported."""
        from agentic_studio.mcp_document.tools import extract_document, batch_extract
        assert extract_document is not None
        assert batch_extract is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])