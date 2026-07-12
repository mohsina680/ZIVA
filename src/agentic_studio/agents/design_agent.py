from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import get_chat_model

SYSTEM_PROMPT = """You are a senior web UI/UX designer and frontend design planner.
Your job is to create professional web design outputs from the user's Markdown instruction.

Scope:
- website layouts
- landing pages
- dashboards
- color palettes
- typography systems
- section-by-section UI plans
- CSS design tokens
- frontend implementation guidance

Rules:
- Focus only on web/design/documentation/coding.
- Do not discuss VMs, servers, Docker Swarm, or unrelated infrastructure.
- Produce practical design output that a developer can implement.
- When creating files, use this exact syntax:

```file path=designs/example.md
file content here
```
"""


def run_design_agent(runbook_text: str, rag_context: str) -> str:
    llm = get_chat_model(temperature=0.35)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"RAG CONTEXT:\n{rag_context}\n\nMARKDOWN INSTRUCTION:\n{runbook_text}"),
    ])
    return str(response.content)
