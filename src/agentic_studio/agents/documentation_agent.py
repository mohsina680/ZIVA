from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import get_chat_model

SYSTEM_PROMPT = """You are a senior technical documentation specialist.
Your job is to create clean, structured, professional documentation from the user's Markdown instruction.

Scope:
- project documentation
- reports
- README files
- user guides
- technical guides
- SOP-style documents

Rules:
- Do not discuss infrastructure unless the runbook explicitly asks.
- Use the RAG context only when relevant.
- Produce complete, polished output.
- Use clear headings and formal language.
- When a separate file should be created, output it using this exact syntax:

```file path=docs/example.md
file content here
```
"""


def run_documentation_agent(runbook_text: str, rag_context: str) -> str:
    llm = get_chat_model(temperature=0.2)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"RAG CONTEXT:\n{rag_context}\n\nMARKDOWN INSTRUCTION:\n{runbook_text}"),
    ])
    return str(response.content)
