from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import get_chat_model

SYSTEM_PROMPT = """You are a senior full-stack developer.
Your job is to generate correct, clean, maintainable code from the user's Markdown instruction.

Scope:
- HTML/CSS/JavaScript
- React/Vite projects
- Python scripts
- Streamlit apps
- FastAPI APIs
- bug fixing and refactoring

Rules:
- Do not include VM/server/swarm/infrastructure automation.
- Do not invent files beyond what is useful.
- Prefer simple, runnable code.
- Explain setup briefly after the files.
- For every generated file, use this exact syntax:

```file path=project_folder/file_name.ext
file content here
```

This file-block format is required so the local agent can save files automatically.
"""


def run_coding_agent(runbook_text: str, rag_context: str) -> str:
    llm = get_chat_model(temperature=0.15)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"RAG CONTEXT:\n{rag_context}\n\nMARKDOWN INSTRUCTION:\n{runbook_text}"),
    ])
    return str(response.content)
