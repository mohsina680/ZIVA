from __future__ import annotations

from src.agentic_studio.llm import get_chat_model
from langchain_core.messages import HumanMessage


def main() -> None:
    llm = get_chat_model(temperature=0)
    response = llm.invoke([HumanMessage(content="Reply with exactly: model-ok")])
    print(response.content)


if __name__ == "__main__":
    main()
