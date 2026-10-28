
from fastapi import APIRouter, HTTPException, status
from openai import OpenAIError

from app.memory.service import (
    conversation_exists,
    create_conversation,
    get_conversation_context,
    get_fused_memory_context,
    save_message,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import get_ai_service

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to Atles",
    description=(
        "Processes the user message through the configured AI provider, "
        "retrieves relevant long-term memory, and maintains conversation history."
    ),
)
async def chat_endpoint(
    payload: ChatRequest,
) -> ChatResponse:
    try:
        # Create a new conversation or validate the existing one.
        if payload.conversation_id is None:
            conversation_id = create_conversation()
        else:
            conversation_id = payload.conversation_id

            if not conversation_exists(conversation_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Conversation {conversation_id} "
                        "does not exist."
                    ),
                )

        # Retrieve recent messages from the conversation.
        conversation_messages = get_conversation_context(
            conversation_id=conversation_id,
            limit=20,
        )

        # Retrieve combined keyword and semantic long-term memory.
        memory_context = get_fused_memory_context(
            query=payload.message,
            limit=5,
        )

        # Select the configured AI provider.
        service = get_ai_service()

        # Generate a response using the user's message,
        # retrieved memories, and conversation history.
        reply = await service.generate_response(
            payload.message,
            memory_context,
            conversation_messages,
        )

        # Save the user message and assistant response.
        save_message(
            conversation_id=conversation_id,
            role="user",
            content=payload.message,
        )

        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=reply,
        )

        return ChatResponse(
            response=reply,
            conversation_id=conversation_id,
        )

    except HTTPException:
        raise

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(val_err),
        ) from val_err

    except (RuntimeError, OpenAIError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to obtain AI response: {exc}",
        ) from exc
