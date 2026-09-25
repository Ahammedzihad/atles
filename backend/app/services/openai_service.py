from typing import Any

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings


class OpenAIService:
    """Service encapsulating interactions with the OpenAI Responses API."""

    def __init__(self, api_key: str | None = None):
        self._explicit_key = api_key
        self._client: AsyncOpenAI | None = None
        self._last_used_key: str | None = None

    def get_client(self) -> AsyncOpenAI:
        current_key = (
            self._explicit_key
            if self._explicit_key and self._explicit_key.strip()
            else settings.OPENAI_API_KEY
        )

        if not current_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured in backend/.env. "
                "Please configure a valid API key to enable AI responses."
            )

        if (
            self._client is None
            or self._last_used_key != current_key
        ):
            self._last_used_key = current_key
            self._client = AsyncOpenAI(
                api_key=current_key
            )

        return self._client

    async def generate_response(
        self,
        message: str,
        memory_context: str = "",
        conversation_messages: list[dict[str, Any]] | None = None,
    ) -> str:
        client = self.get_client()

        if memory_context:
            instructions = (
                "You are Atles, an intelligent personal AI assistant.\n\n"
                "Relevant long-term memory from previous interactions:\n"
                f"{memory_context}"
            )
        else:
            instructions = (
                "You are Atles, an intelligent personal AI assistant.\n\n"
                "No relevant previous memory was retrieved."
            )

        input_messages: list[dict[str, str]] = []

        if conversation_messages:
            for conversation_message in conversation_messages:
                role = conversation_message.get("role")
                content = conversation_message.get("content")

                if role in {"user", "assistant"} and content:
                    input_messages.append(
                        {
                            "role": role,
                            "content": content,
                        }
                    )

        input_messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        try:
            response = await client.responses.create(
                model=settings.OPENAI_MODEL,
                input=input_messages,
                instructions=instructions,
            )

            reply = response.output_text

            if not reply:
                reply = (
                    "I received your message, "
                    "but no text response was produced."
                )

            return reply

        except OpenAIError as err:
            raise RuntimeError(
                f"OpenAI service error: {err}"
            ) from err


openai_service = OpenAIService()