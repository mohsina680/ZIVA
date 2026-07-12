from __future__ import annotations

from langchain_openai import ChatOpenAI
from .config import get_settings


def get_chat_model(temperature: float = 0.2) -> ChatOpenAI:
    """Create an OpenAI-compatible local chat model client.

    Works with Ollama OpenAI-compatible endpoint or LM Studio.
    """
    settings = get_settings()
    return ChatOpenAI(
        model=settings.text_model,
        base_url=settings.local_llm_base_url,
        api_key=settings.local_llm_api_key,
        temperature=temperature,
    )
