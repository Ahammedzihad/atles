import os
from typing import Any

from app.core.config import settings
from app.services.ollama_service import OllamaService, ollama_service
from app.services.openai_service import OpenAIService, openai_service


def get_ai_service(provider: str | None = None) -> Any:
    """
    Resolve and return the configured AI service implementation.
    Defaults to settings.AI_PROVIDER (or environment variable AI_PROVIDER).
    """
    selected_provider = (
        provider or os.getenv("AI_PROVIDER", settings.AI_PROVIDER)
    ).lower().strip()

    if selected_provider == "ollama":
        return ollama_service
    elif selected_provider == "openai":
        return openai_service
    else:
        raise ValueError(
            f"Unsupported AI_PROVIDER: '{selected_provider}'. "
            "Supported providers are 'ollama' and 'openai'."
        )


__all__ = [
    "OllamaService",
    "OpenAIService",
    "get_ai_service",
    "ollama_service",
    "openai_service",
]
