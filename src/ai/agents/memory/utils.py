from gradio import ChatMessage
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    TextPart,
    UserPromptPart,
)

from src.ui import ChatMessage, History


def to_pydantic_history(chat_history: History) -> list[ModelMessage]:
    """
    Convert Gradio chat history to Pydantic AI message format.
    
    This utility handles the transformation between Gradio's ChatMessage format
    and Pydantic AI's ModelMessage format, ensuring compatibility with the
    agent framework.
    
    Args:
        chat_history: List of ChatMessage objects from Gradio interface
        
    Returns:
        List of ModelMessage objects compatible with Pydantic AI agents
        
    Note:
        Future enhancement: Add intelligent message trimming to fit model context length
    """
    pydantic_history = []
    
    for message in chat_history:
        # Handle both ChatMessage objects and dict formats
        if not isinstance(message, ChatMessage):
            assert message.get("role") and message.get(
                "content"
            ), "Message must have 'role' and 'content' keys"

            message = ChatMessage(
                content=message.get("content"), 
                role=message.get("role")
            )

        # Convert to Pydantic AI message format
        pydantic_history.append(
            {
                "role": "model" if message.role == "assistant" else message.role,
                "parts": [
                    (
                        UserPromptPart(
                            content=message.content,  # type: ignore[call-arg]
                            part_kind="user-prompt",
                        )
                        if message.role == "user"
                        else TextPart(
                            content=message.content,  # type: ignore[call-arg]
                            part_kind="text",
                        )
                    )
                ],
                "kind": "request" if message.role == "user" else "response",
            }
        )
        
    return ModelMessagesTypeAdapter.validate_python(pydantic_history)
