from typing import Any

import httpx

from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings through local Ollama."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str = "nomic-embed-text",
        timeout: float | None = None,
    ):
        self._explicit_base_url = base_url
        self._explicit_model = model
        self._explicit_timeout = timeout

    @property
    def base_url(self) -> str:
        url = (
            self._explicit_base_url
            or settings.OLLAMA_BASE_URL
        )

        return url.rstrip("/")

    @property
    def model(self) -> str:
        return self._explicit_model

    @property
    def timeout(self) -> float:
        if self._explicit_timeout is not None:
            return self._explicit_timeout

        return settings.OLLAMA_TIMEOUT

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate an embedding vector asynchronously."""

        if not text or not text.strip():
            raise ValueError(
                "Text must not be empty."
            )

        payload = {
            "model": self.model,
            "prompt": text,
        }

        endpoint = (
            f"{self.base_url}/api/embeddings"
        )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                )

                response.raise_for_status()

                data: dict[str, Any] = response.json()

        except httpx.ConnectError as err:
            raise RuntimeError(
                f"Could not connect to Ollama at "
                f"{self.base_url}. "
                "Ensure Ollama is running locally."
            ) from err

        except httpx.TimeoutException as err:
            raise RuntimeError(
                f"Ollama embedding request timed out "
                f"after {self.timeout} seconds."
            ) from err

        except httpx.HTTPStatusError as err:
            raise RuntimeError(
                f"Ollama embedding request returned "
                f"HTTP error {err.response.status_code}: "
                f"{err.response.text}"
            ) from err

        except Exception as err:
            raise RuntimeError(
                f"Ollama embedding service error: {err}"
            ) from err

        embedding = data.get("embedding")

        if not isinstance(embedding, list):
            raise RuntimeError(
                "Ollama returned an invalid embedding response."
            )

        if not embedding:
            raise RuntimeError(
                "Ollama returned an empty embedding."
            )

        try:
            return [
                float(value)
                for value in embedding
            ]
        except (TypeError, ValueError) as err:
            raise RuntimeError(
                "Ollama returned an embedding containing "
                "invalid numeric values."
            ) from err

    def embed_sync(
        self,
        text: str,
    ) -> list[float]:
        """Generate an embedding vector synchronously.

        This method uses a synchronous HTTP client so it is safe
        to call from both normal synchronous code and code that is
        already running inside an asyncio event loop.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text must not be empty."
            )

        payload = {
            "model": self.model,
            "prompt": text,
        }

        endpoint = (
            f"{self.base_url}/api/embeddings"
        )

        try:
            with httpx.Client(
                timeout=self.timeout
            ) as client:
                response = client.post(
                    endpoint,
                    json=payload,
                )

                response.raise_for_status()

                data: dict[str, Any] = response.json()

        except httpx.ConnectError as err:
            raise RuntimeError(
                f"Could not connect to Ollama at "
                f"{self.base_url}. "
                "Ensure Ollama is running locally."
            ) from err

        except httpx.TimeoutException as err:
            raise RuntimeError(
                f"Ollama embedding request timed out "
                f"after {self.timeout} seconds."
            ) from err

        except httpx.HTTPStatusError as err:
            raise RuntimeError(
                f"Ollama embedding request returned "
                f"HTTP error {err.response.status_code}: "
                f"{err.response.text}"
            ) from err

        except Exception as err:
            raise RuntimeError(
                f"Ollama embedding service error: {err}"
            ) from err

        embedding = data.get("embedding")

        if not isinstance(embedding, list):
            raise RuntimeError(
                "Ollama returned an invalid embedding response."
            )

        if not embedding:
            raise RuntimeError(
                "Ollama returned an empty embedding."
            )

        try:
            return [
                float(value)
                for value in embedding
            ]
        except (TypeError, ValueError) as err:
            raise RuntimeError(
                "Ollama returned an embedding containing "
                "invalid numeric values."
            ) from err


embedding_service = EmbeddingService()