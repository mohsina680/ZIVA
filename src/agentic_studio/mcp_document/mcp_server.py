"""
ZIVA Document Extractor MCP Server.

This module provides an MCP (Model Context Protocol) server
that exposes document extraction tools to Claude Code.
"""
from __future__ import annotations

from typing import Optional, List, Any
from pathlib import Path
import json

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class DocumentExtractorMCPServer:
    """
    MCP server for document extraction.

    Exposes the following tools:
    - extract_document: Extract text from a single document
    - batch_extract_documents: Extract text from multiple documents
    - get_extractor_status: Check which extractors are available
    - analyze_document: Get document metadata without extraction
    - clear_cache: Clear the extraction cache
    """

    def __init__(self):
        """Initialize the MCP server."""
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP library not installed. Install with: pip install mcp"
            )

        self.server = Server("ziva-document-extractor")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP request handlers."""
        from mcp.types import (
            ListToolsRequest,
            ListToolsResult,
            CallToolRequest,
            CallToolResult,
        )

        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available MCP tools."""
            return ListToolsResult(tools=self._get_tools())

        @self.server.call_tool()
        async def call_tool(
            name: str,
            arguments: dict
        ) -> List[TextContent]:
            """Handle tool calls."""
            result = await self._handle_tool(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    def _get_tools(self) -> List[Tool]:
        """Get list of available tools."""
        return [
            Tool(
                name="extract_document",
                description=(
                    "Extract text from documents using intelligent cascading OCR. "
                    "Tries extractors in order: Tesseract → Docling → EasyOCR → Surya. "
                    "Returns extracted text with confidence score. 100% free and local."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to PDF or image file"
                        },
                        "force_extractor": {
                            "type": "string",
                            "enum": ["tesseract", "docling", "easyocr", "surya", "auto"],
                            "default": "auto",
                            "description": "Force a specific extractor"
                        },
                        "min_confidence": {
                            "type": "number",
                            "default": 0.7,
                            "description": "Minimum confidence threshold (0-1)"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="batch_extract_documents",
                description="Extract text from multiple documents with intelligent routing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file paths"
                        },
                        "parallel": {
                            "type": "boolean",
                            "default": False,
                            "description": "Process in parallel (faster but uses more resources)"
                        }
                    },
                    "required": ["file_paths"]
                }
            ),
            Tool(
                name="get_extractor_status",
                description="Check which document extractors are installed and available",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="analyze_document",
                description="Analyze a document to determine its type and recommended extraction strategy",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to PDF or image file"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="clear_extraction_cache",
                description="Clear the document extraction cache",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_cache_stats",
                description="Get document extraction cache statistics",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

    async def _handle_tool(self, name: str, arguments: dict) -> dict:
        """Handle a tool call."""
        from ..extractor import DocumentExtractor, get_document_extractor

        extractor = get_document_extractor()

        if name == "extract_document":
            result = extractor.extract(
                file_path=arguments["file_path"],
                force_extractor=arguments.get("force_extractor", "auto"),
                min_confidence=arguments.get("min_confidence", 0.7)
            )
            return result.to_dict()

        elif name == "batch_extract_documents":
            results = extractor.extract_batch(
                file_paths=arguments["file_paths"],
                parallel=arguments.get("parallel", False)
            )
            return {
                "total": len(results),
                "results": [r.to_dict() for r in results]
            }

        elif name == "get_extractor_status":
            return {
                "available_extractors": extractor.get_available_extractors(),
                "cache_stats": extractor.get_cache_stats()
            }

        elif name == "analyze_document":
            doc_info = extractor.analyze(arguments["file_path"])
            return {
                "document_type": doc_info.document_type.value,
                "page_count": doc_info.page_count,
                "is_searchable": doc_info.is_searchable,
                "estimated_quality": doc_info.estimated_quality,
                "file_size_bytes": doc_info.file_size_bytes
            }

        elif name == "clear_extraction_cache":
            count = extractor.cache.clear()
            return {"cleared_entries": count}

        elif name == "get_cache_stats":
            return extractor.get_cache_stats()

        else:
            return {"error": f"Unknown tool: {name}"}

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def create_mcp_server() -> Optional[DocumentExtractorMCPServer]:
    """
    Create an MCP server instance.

    Returns None if MCP is not available.
    """
    if not MCP_AVAILABLE:
        return None
    return DocumentExtractorMCPServer()


if __name__ == "__main__":
    # Run the MCP server
    server = create_mcp_server()
    if server:
        import asyncio
        asyncio.run(server.run())
    else:
        print("MCP not available. Install with: pip install mcp")