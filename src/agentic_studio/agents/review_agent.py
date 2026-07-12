from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from ..llm import get_chat_model

SYSTEM_PROMPT = """You are a strict reviewer for a local documentation, coding, and web-design agent.
Review the generated output against the original instruction.

Return:
1. Pass/Fail
2. Missing requirements
3. Quality issues
4. Suggested improvements
5. Final short verdict

Do not introduce infrastructure topics unless the original instruction asks for them.
"""


def run_review_agent(runbook_text: str, generated_output: str) -> str:
    llm = get_chat_model(temperature=0.1)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"ORIGINAL INSTRUCTION:\n{runbook_text}\n\nGENERATED OUTPUT:\n{generated_output}"),
    ])
    return str(response.content)
