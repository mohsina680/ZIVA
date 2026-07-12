from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import get_chat_model
from ..mcp_document import extract_document, DocumentExtractor

SYSTEM_PROMPT = """You are a document extraction specialist for ZIVA Agent.
Extract text from documents using intelligent OCR with cascading fallback.

Available extractors (in order):
1. Docling - best for native/searchable PDFs
2. Tesseract - system OCR, fast
3. EasyOCR - pure Python OCR
4. Surya - Microsoft OCR

Process:
1. Get file path from task
2. Auto-detect document type
3. Extract with cascading extractors until confidence >= 0.7
4. Return structured output

Output must include:
- extracted text
- confidence score
- which extractor was used
- page count
"""


def run_document_agent(runbook_text: str, rag_context: str = "") -> str:
    llm = get_chat_model(temperature=0.1)

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"RAG CONTEXT:\n{rag_context}\n\nTASK:\n{runbook_text}"),
    ])

    return str(response.content)


def extract_document_text(file_path: str, force_extractor: str = None) -> dict:
    """Direct document extraction function."""
    extractor = DocumentExtractor()
    result = extractor.extract(file_path, force_extractor=force_extractor)
    return result.to_dict()