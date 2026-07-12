from __future__ import annotations

from typing import TypedDict, Literal, Optional, List, Dict, Any

TaskType = Literal["documentation", "coding", "web_design", "document_extraction", "unknown"]


class AgentState(TypedDict, total=False):
    runbook_path: str
    runbook_text: str
    user_request: str
    task_type: TaskType
    rag_context: str
    generated_output: str
    review_output: str
    saved_files: List[str]
    errors: List[str]
    metadata: Dict[str, Any]