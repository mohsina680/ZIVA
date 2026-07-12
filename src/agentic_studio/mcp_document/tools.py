"""
MCP tool bindings for ZIVA Agent.

These tools can be used directly within the agent workflow
without running the full MCP server.
"""
from __future__ import annotations

from typing import Optional, List, Any

try:
    from langchain_core.tools import BaseTool
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseModel = object


# Document extraction result schema for tools
if LANGCHAIN_AVAILABLE:
    class ExtractDocumentInput(BaseModel):
        """Input schema for extract document tool."""
        file_path: str = Field(description="Path to PDF or image file")
        force_extractor: Optional[str] = Field(
            default="auto",
            description="Force extractor: tesseract, docling, easyocr, surya, or auto"
        )
        min_confidence: float = Field(
            default=0.7,
            description="Minimum confidence threshold (0-1)"
        )

    class BatchExtractInput(BaseModel):
        """Input schema for batch extract tool."""
        file_paths: List[str] = Field(description="List of file paths")
        parallel: bool = Field(default=False, description="Process in parallel")

    class AnalyzeDocumentInput(BaseModel):
        """Input schema for analyze document tool."""
        file_path: str = Field(description="Path to document")


if LANGCHAIN_AVAILABLE:
    class ExtractDocumentTool(BaseTool):
        """LangChain tool for document extraction."""

        name: str = "extract_document"
        description: str = (
            "Extract text from documents using intelligent cascading OCR. "
            "Tries extractors in order: Tesseract → Docling → EasyOCR → Surya. "
            "Returns extracted text with confidence score. 100% free and local."
        )
        args_schema: type = ExtractDocumentInput

        def _run(
            self,
            file_path: str,
            force_extractor: str = "auto",
            min_confidence: float = 0.7
        ) -> str:
            """Run the tool synchronously."""
            from ..extractor import get_document_extractor

            extractor = get_document_extractor()
            result = extractor.extract(
                file_path=file_path,
                force_extractor=force_extractor if force_extractor != "auto" else None,
                min_confidence=min_confidence
            )

            return self._format_result(result)

        async def _arun(
            self,
            file_path: str,
            force_extractor: str = "auto",
            min_confidence: float = 0.7
        ) -> str:
            """Run the tool asynchronously."""
            return self._run(file_path, force_extractor, min_confidence)

        @staticmethod
        def _format_result(result) -> str:
            """Format extraction result for display."""
            import json

            output = {
                "status": "success" if result.is_successful() else "failed",
                "extractor_used": result.extractor_name,
                "confidence": f"{result.confidence:.2f}",
                "page_count": result.page_count,
                "extraction_time_ms": result.extraction_time_ms,
                "cache_hit": result.cache_hit,
                "text_length": len(result.text),
                "text_preview": result.text[:500] + "..." if len(result.text) > 500 else result.text
            }

            if result.error:
                output["error"] = result.error

            return json.dumps(output, indent=2)


    class BatchExtractTool(BaseTool):
        """LangChain tool for batch document extraction."""

        name: str = "batch_extract_documents"
        description: str = "Extract text from multiple documents with intelligent routing"
        args_schema: type = BatchExtractInput

        def _run(
            self,
            file_paths: List[str],
            parallel: bool = False
        ) -> str:
            """Run the tool synchronously."""
            from ..extractor import get_document_extractor

            extractor = get_document_extractor()
            results = extractor.extract_batch(
                file_paths=file_paths,
                parallel=parallel
            )

            return self._format_results(results)

        async def _arun(
            self,
            file_paths: List[str],
            parallel: bool = False
        ) -> str:
            """Run the tool asynchronously."""
            return self._run(file_paths, parallel)

        @staticmethod
        def _format_results(results: list) -> str:
            """Format batch extraction results."""
            import json

            output = {
                "total_documents": len(results),
                "successful": sum(1 for r in results if r.is_successful()),
                "failed": sum(1 for r in results if not r.is_successful()),
                "results": [
                    {
                        "status": "success" if r.is_successful() else "failed",
                        "extractor": r.extractor_name,
                        "confidence": r.confidence,
                        "text_length": len(r.text),
                        "error": r.error
                    }
                    for r in results
                ]
            }

            return json.dumps(output, indent=2)


    class AnalyzeDocumentTool(BaseTool):
        """LangChain tool for document analysis."""

        name: str = "analyze_document"
        description: str = "Analyze a document to determine its type and recommended extraction strategy"
        args_schema: type = AnalyzeDocumentInput

        def _run(self, file_path: str) -> str:
            """Run the tool synchronously."""
            from ..extractor import get_document_extractor
            from ..analyzers.document_analyzer import DocumentAnalyzer

            extractor = get_document_extractor()
            doc_info = extractor.analyze(file_path)

            # Get recommended extractors
            analyzer = DocumentAnalyzer()
            recommended = analyzer.get_recommended_extractors(doc_info)

            import json
            return json.dumps({
                "document_type": doc_info.document_type.value,
                "page_count": doc_info.page_count,
                "is_searchable": doc_info.is_searchable,
                "estimated_quality": doc_info.estimated_quality,
                "file_size_mb": round(doc_info.file_size_bytes / (1024 * 1024), 2),
                "recommended_extractors": recommended
            }, indent=2)

        async def _arun(self, file_path: str) -> str:
            """Run the tool asynchronously."""
            return self._run(file_path)


    # Tool registry
    TOOLS = [
        ExtractDocumentTool(),
        BatchExtractTool(),
        AnalyzeDocumentTool(),
    ]

    def get_mcp_tools() -> list:
        """Get all MCP tools for use in LangChain."""
        return TOOLS

else:
    def get_mcp_tools() -> list:
        """Return empty list if LangChain not available."""
        return []


def extract_document(
    file_path: str,
    force_extractor: Optional[str] = None,
    min_confidence: float = 0.7
) -> dict:
    """
    Direct function to extract text from a document.

    Provides a simpler interface than the extractor class.

    Args:
        file_path: Path to PDF or image file
        force_extractor: Force a specific extractor
        min_confidence: Minimum confidence threshold

    Returns:
        Dictionary with extraction results
    """
    from .extractor import get_document_extractor

    extractor = get_document_extractor()
    result = extractor.extract(
        file_path=file_path,
        force_extractor=force_extractor,
        min_confidence=min_confidence
    )
    return result.to_dict()


def batch_extract(
    file_paths: List[str],
    parallel: bool = False
) -> List[dict]:
    """
    Direct function to extract text from multiple documents.

    Args:
        file_paths: List of file paths
        parallel: Process in parallel

    Returns:
        List of result dictionaries
    """
    from .extractor import get_document_extractor

    extractor = get_document_extractor()
    results = extractor.extract_batch(
        file_paths=file_paths,
        parallel=parallel
    )
    return [r.to_dict() for r in results]