from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import get_chat_model
from ..prompts import build_agent_user_message

SYSTEM_PROMPT = """You are a senior full-stack developer.
Your job is to generate correct, clean, maintainable code from the user's Markdown instruction.

Scope:
- HTML/CSS/JavaScript
- Node.js projects
- TypeScript projects
- React/Vite projects
- Python scripts
- Streamlit apps
- FastAPI APIs
- bug fixing and refactoring

Rules:
- Do not include VM/server/swarm/infrastructure automation.
- Do not invent files beyond what is useful.
- Prefer simple, runnable code.
- If the task is UI related, prioritize a polished, modern, responsive interface.
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
        HumanMessage(content=build_agent_user_message("MARKDOWN INSTRUCTION", runbook_text, rag_context)),
    ])
    return str(response.content)
