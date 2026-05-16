"""Chat with gpt-oss via AnyLLM (used by Flask and any.py)."""

from __future__ import annotations

import anyllm

DEFAULT_MODEL = "gpt-oss:120b-cloud"


def extract_text(response: object) -> str:
    if isinstance(response, str):
        return response
    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content
    return str(response)


def chat_with_model(
    message: str,
    *,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Send a user message and return the model answer."""
    response = anyllm.chat(message, model=model)
    return {
        "answer": extract_text(response),
        "model": getattr(response, "model", model),
    }
