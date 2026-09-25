import os
from typing import Any

import httpx

from app.core.config import settings


class OllamaService:
    """Service encapsulating interactions with local Ollama API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        system_prompt: str | None = None,
        timeout: float | None = None,
    ):
        self._explicit_base_url = base_url
        self._explicit_model = model
        self._explicit_system_prompt = system_prompt
        self._explicit_timeout = timeout

    @property
    def base_url(self) -> str:
        url = self._explicit_base_url or os.getenv(
            "OLLAMA_BASE_URL",
            settings.OLLAMA_BASE_URL,
        )
        return url.rstrip("/")

    @property
    def model(self) -> str:
        return self._explicit_model or os.getenv(
            "OLLAMA_MODEL",
            settings.OLLAMA_MODEL,
        )

    @property
    def system_prompt(self) -> str:
        return self._explicit_system_prompt or os.getenv(
            "ATLES_SYSTEM_PROMPT",
            settings.ATLES_SYSTEM_PROMPT,
        )

    @property
    def timeout(self) -> float:
        if self._explicit_timeout is not None:
            return self._explicit_timeout

        env_timeout = os.getenv("OLLAMA_TIMEOUT")

        if env_timeout:
            try:
                return float(env_timeout)
            except ValueError:
                pass

        return settings.OLLAMA_TIMEOUT

    async def generate_response(
        self,
        message: str,
        memory_context: str = "",
        conversation_messages: list[dict[str, Any]] | None = None,
    ) -> str:
        """
        Send the system prompt, memory context, conversation history,
        and current user message to Ollama.
        """
        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]

        if memory_context:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Relevant long-term memory from previous interactions:\n"
                        f"{memory_context}"
                    ),
                }
            )

        if conversation_messages:
            for conversation_message in conversation_messages:
                role = conversation_message.get("role")
                content = conversation_message.get("content")

                if role in {"user", "assistant"} and content:
                    messages.append(
                        {
                            "role": role,
                            "content": content,
                        }
                    )

        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        endpoint = f"{self.base_url}/api/chat"

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

        except httpx.ConnectError as err:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Ensure Ollama is running locally."
            ) from err

        except httpx.TimeoutException as err:
            raise RuntimeError(
                f"Ollama request timed out after "
                f"{self.timeout} seconds."
            ) from err

        except httpx.HTTPStatusError as err:
            raise RuntimeError(
                f"Ollama returned HTTP error "
                f"{err.response.status_code}: "
                f"{err.response.text}"
            ) from err

        except Exception as err:
            raise RuntimeError(
                f"Ollama service error: {err}"
            ) from err

        reply = data.get(
            "message",
            {},
        ).get(
            "content",
            "",
        )

        if not reply or not reply.strip():
            reply = (
                "I received your message, "
                "but no text response was produced."
            )

        return reply.strip()


ollama_service = OllamaService()