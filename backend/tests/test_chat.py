import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.services.ollama_service import OllamaService
from main import app


client = TestClient(app)


def test_chat_success_mocked_ollama():
    """Test successful POST /chat with fused memory retrieval."""
    mock_reply = (
        "Hello! I am Atles, your personal AI assistant. "
        "How can I help you today?"
    )

    fused_memory = (
        "[test] Atles Memory v1 test\n"
        "[semantic] Atles semantic memory test"
    )

    with patch(
        "app.api.routes.chat.get_fused_memory_context",
        return_value=fused_memory,
    ) as mock_memory, patch(
        "app.services.ollama_service.OllamaService.generate_response",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = mock_reply

        response = client.post(
            "/chat",
            json={"message": "Tell me about Atles Memory"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["response"] == mock_reply

        assert isinstance(
            data["conversation_id"],
            int,
        )

        mock_memory.assert_called_once_with(
            query="Tell me about Atles Memory",
            limit=5,
        )

        mock_generate.assert_awaited_once()

        call_args = mock_generate.call_args.args

        assert call_args[0] == (
            "Tell me about Atles Memory"
        )

        assert call_args[1] == fused_memory

        assert call_args[2] == []


def test_chat_success_mocked_openai(monkeypatch):
    """Test POST /chat with OpenAI provider and fused memory."""
    monkeypatch.setenv(
        "AI_PROVIDER",
        "openai",
    )

    mock_reply = "Hello from Atles via OpenAI!"

    fused_memory = (
        "[test] Atles Memory v1 test\n"
        "[semantic] Atles semantic memory test"
    )

    with patch(
        "app.api.routes.chat.get_fused_memory_context",
        return_value=fused_memory,
    ) as mock_memory, patch(
        "app.services.openai_service.OpenAIService.generate_response",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = mock_reply

        response = client.post(
            "/chat",
            json={"message": "Tell me about Atles Memory"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["response"] == mock_reply

        assert isinstance(
            data["conversation_id"],
            int,
        )

        mock_memory.assert_called_once_with(
            query="Tell me about Atles Memory",
            limit=5,
        )

        mock_generate.assert_awaited_once()

        call_args = mock_generate.call_args.args

        assert call_args[0] == (
            "Tell me about Atles Memory"
        )

        assert call_args[1] == fused_memory

        assert call_args[2] == []


def test_chat_continues_existing_conversation():
    """Test that Atles loads previous messages in an existing conversation."""
    mock_reply = "Your project is called Atles."

    with patch(
        "app.api.routes.chat.get_fused_memory_context",
        return_value="",
    ) as mock_memory, patch(
        "app.services.ollama_service.OllamaService.generate_response",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = mock_reply

        first_response = client.post(
            "/chat",
            json={
                "message": "My project is called Atles."
            },
        )

        assert first_response.status_code == 200

        conversation_id = first_response.json()[
            "conversation_id"
        ]

        mock_generate.reset_mock()
        mock_memory.reset_mock()

        second_response = client.post(
            "/chat",
            json={
                "message": "What is my project called?",
                "conversation_id": conversation_id,
            },
        )

        assert second_response.status_code == 200

        second_data = second_response.json()

        assert second_data["response"] == mock_reply

        assert (
            second_data["conversation_id"]
            == conversation_id
        )

        mock_memory.assert_called_once_with(
            query="What is my project called?",
            limit=5,
        )

        mock_generate.assert_awaited_once()

        call_args = mock_generate.call_args.args

        assert call_args[0] == (
            "What is my project called?"
        )

        assert isinstance(
            call_args[2],
            list,
        )

        assert len(call_args[2]) == 2

        assert call_args[2][0]["role"] == "user"

        assert call_args[2][0]["content"] == (
            "My project is called Atles."
        )

        assert call_args[2][1]["role"] == "assistant"

        assert call_args[2][1]["content"] == (
            mock_reply
        )


def test_chat_fused_memory_only():
    """Test that fused memory is passed directly to the AI service."""
    mock_reply = "I remember that Atles is your personal AI project."

    fused_memory = (
        "[project] Atles is the user's personal AI project."
    )

    with patch(
        "app.api.routes.chat.get_fused_memory_context",
        return_value=fused_memory,
    ) as mock_memory, patch(
        "app.services.ollama_service.OllamaService.generate_response",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = mock_reply

        response = client.post(
            "/chat",
            json={
                "message": "Tell me about my AI project"
            },
        )

        assert response.status_code == 200

        assert response.json()["response"] == mock_reply

        mock_memory.assert_called_once_with(
            query="Tell me about my AI project",
            limit=5,
        )

        mock_generate.assert_awaited_once()

        call_args = mock_generate.call_args.args

        assert call_args[1] == fused_memory


def test_chat_no_memory():
    """Test that chat works when fused memory returns no results."""
    mock_reply = "Hello from Atles."

    with patch(
        "app.api.routes.chat.get_fused_memory_context",
        return_value="",
    ) as mock_memory, patch(
        "app.services.ollama_service.OllamaService.generate_response",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = mock_reply

        response = client.post(
            "/chat",
            json={"message": "Hello"},
        )

        assert response.status_code == 200

        assert response.json()["response"] == mock_reply

        mock_memory.assert_called_once_with(
            query="Hello",
            limit=5,
        )

        mock_generate.assert_awaited_once()

        call_args = mock_generate.call_args.args

        assert call_args[1] == ""


def test_chat_invalid_conversation_id():
    """Test that an unknown conversation ID returns 404."""
    response = client.post(
        "/chat",
        json={
            "message": "Hello",
            "conversation_id": 999999999,
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        "does not exist"
        in data["detail"]
    )


def test_chat_unsupported_provider(monkeypatch):
    """Test unsupported AI provider."""
    monkeypatch.setenv(
        "AI_PROVIDER",
        "unsupported_provider",
    )

    response = client.post(
        "/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 503

    data = response.json()

    assert "Unsupported AI_PROVIDER" in data["detail"]


def test_chat_upstream_service_error():
    """Test POST /chat returns 502 when AI service fails."""
    with patch(
        "app.api.routes.chat.get_fused_memory_context",
        return_value="",
    ), patch(
        "app.services.ollama_service.OllamaService.generate_response",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.side_effect = RuntimeError(
            "Could not connect to Ollama at "
            "http://127.0.0.1:11434."
        )

        response = client.post(
            "/chat",
            json={"message": "Hello"},
        )

        assert response.status_code == 502

        data = response.json()

        assert "Could not connect to Ollama" in (
            data["detail"]
        )


def test_chat_invalid_payload():
    """Test invalid chat payload."""
    response = client.post(
        "/chat",
        json={},
    )

    assert response.status_code == 422

    response = client.post(
        "/chat",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_ollama_service_generate_response_success():
    """Unit test OllamaService payload and response extraction."""
    service = OllamaService(
        base_url="http://127.0.0.1:11434",
        model="qwen3:4b",
        system_prompt="You are Atles.",
        timeout=10.0,
    )

    mock_response = MagicMock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "model": "qwen3:4b",
        "message": {
            "role": "assistant",
            "content": "I am Atles, ready to assist.",
        },
    }

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
    ) as mock_post:
        mock_post.return_value = mock_response

        reply = asyncio.run(
            service.generate_response("Hello")
        )

        assert reply == (
            "I am Atles, ready to assist."
        )

        mock_post.assert_awaited_once()

        call_args, call_kwargs = (
            mock_post.call_args
        )

        assert call_args[0] == (
            "http://127.0.0.1:11434/api/chat"
        )

        payload = call_kwargs["json"]

        assert payload["model"] == "qwen3:4b"

        assert payload["stream"] is False

        assert payload["messages"][0] == {
            "role": "system",
            "content": "You are Atles.",
        }

        assert payload["messages"][1] == {
            "role": "user",
            "content": "Hello",
        }


def test_ollama_service_memory_context():
    """Test Ollama receives fused long-term memory context."""
    service = OllamaService(
        base_url="http://127.0.0.1:11434",
        model="qwen3:4b",
        system_prompt="You are Atles.",
        timeout=10.0,
    )

    mock_response = MagicMock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "model": "qwen3:4b",
        "message": {
            "role": "assistant",
            "content": "I remember your project.",
        },
    }

    fused_memory = (
        "[project] Atles is your personal AI project.\n"
        "[preference] User prefers local AI."
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
    ) as mock_post:
        mock_post.return_value = mock_response

        reply = asyncio.run(
            service.generate_response(
                "Tell me about my project.",
                fused_memory,
            )
        )

        assert reply == (
            "I remember your project."
        )

        payload = (
            mock_post.call_args.kwargs["json"]
        )

        assert payload["messages"][0] == {
            "role": "system",
            "content": "You are Atles.",
        }

        assert payload["messages"][1] == {
            "role": "system",
            "content": (
                "Relevant long-term memory from previous interactions:\n"
                f"{fused_memory}"
            ),
        }

        assert payload["messages"][2] == {
            "role": "user",
            "content": "Tell me about my project.",
        }


def test_ollama_service_conversation_history():
    """Test Ollama receives previous conversation messages."""
    service = OllamaService(
        base_url="http://127.0.0.1:11434",
        model="qwen3:4b",
        system_prompt="You are Atles.",
        timeout=10.0,
    )

    mock_response = MagicMock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "model": "qwen3:4b",
        "message": {
            "role": "assistant",
            "content": "Your project is Atles.",
        },
    }

    conversation_messages = [
        {
            "role": "user",
            "content": "My project is called Atles.",
        },
        {
            "role": "assistant",
            "content": "Got it.",
        },
    ]

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
    ) as mock_post:
        mock_post.return_value = mock_response

        reply = asyncio.run(
            service.generate_response(
                "What is my project called?",
                "",
                conversation_messages,
            )
        )

        assert reply == (
            "Your project is Atles."
        )

        payload = (
            mock_post.call_args.kwargs["json"]
        )

        assert payload["messages"][0] == {
            "role": "system",
            "content": "You are Atles.",
        }

        assert payload["messages"][1] == {
            "role": "user",
            "content": (
                "My project is called Atles."
            ),
        }

        assert payload["messages"][2] == {
            "role": "assistant",
            "content": "Got it.",
        }

        assert payload["messages"][3] == {
            "role": "user",
            "content": (
                "What is my project called?"
            ),
        }


def test_ollama_service_connection_error():
    """Test OllamaService connection error."""
    service = OllamaService(
        base_url="http://127.0.0.1:11434",
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
    ) as mock_post:
        mock_post.side_effect = httpx.ConnectError(
            "Connection refused"
        )

        with pytest.raises(
            RuntimeError,
            match="Could not connect to Ollama",
        ):
            asyncio.run(
                service.generate_response("Hello")
            )


def test_ollama_service_timeout():
    """Test OllamaService timeout handling."""
    service = OllamaService(
        base_url="http://127.0.0.1:11434",
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
    ) as mock_post:
        mock_post.side_effect = (
            httpx.TimeoutException(
                "Read timed out"
            )
        )

        with pytest.raises(
            RuntimeError,
            match="timed out",
        ):
            asyncio.run(
                service.generate_response("Hello")
            )