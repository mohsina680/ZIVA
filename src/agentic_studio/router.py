from __future__ import annotations

from .state import TaskType


def classify_task(runbook_text: str, runbook_path: str = "") -> TaskType:
    text = f"{runbook_path}\n{runbook_text}".lower()

    documentation_terms = [
        "documentation", "document", "report", "readme", "sop", "proposal",
        "abstract", "chapter", "manual", "guide", "case study", "project report"
    ]
    coding_terms = [
        "code", "coding", "python", "react", "html", "css", "javascript",
        "typescript", "streamlit", "fastapi", "bug", "feature", "api", "component"
    ]
    design_terms = [
        "design", "ui", "ux", "wireframe", "layout", "theme", "color palette",
        "landing page", "web design", "homepage", "dashboard design", "style guide"
    ]
    # Document extraction terms
    extraction_terms = [
        "extract", "ocr", "scrap", "scan", "pdf to text", "image to text",
        "text from", "read pdf", "ocr extract", "scan extract", "sro",
        "notification", "document extraction"
    ]

    scores = {
        "documentation": sum(term in text for term in documentation_terms),
        "coding": sum(term in text for term in coding_terms),
        "web_design": sum(term in text for term in design_terms),
        "document_extraction": sum(term in text for term in extraction_terms),
    }

    # Path has strong signal
    if "runbooks/documentation" in text:
        scores["documentation"] += 3
    if "runbooks/coding" in text:
        scores["coding"] += 3
    if "runbooks/design" in text:
        scores["web_design"] += 3
    if "runbooks/document_extraction" in text:
        scores["document_extraction"] += 3

    task_type = max(scores, key=scores.get)
    if scores[task_type] == 0:
        return "unknown"
    return task_type