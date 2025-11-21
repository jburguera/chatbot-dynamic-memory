from typing import Literal
from uuid import uuid4

from asyncer import asyncify
from gradio import ChatMessage, State

from src.ai.agents import AgentDependencies
from src.ai.agents.example_agent import example_agent
from src.ai.agents.memory.utils import to_pydantic_history
from src.ai.agents.tools.publications import create_draft_tool, register_tools
from src.ui import History, Usage, create_chat_ui
from src.users.entities.user import CurrentUser

# Available agents for demo purposes
agents = {
    "example_agent": example_agent,
}

# Demo user configuration
current_user = CurrentUser(
    id=uuid4(),
    name="Demo User",
    sector="technology",
    profession="developer",
    language="en",
)


def handle_user_message(
    user_input: str,
    history: History,
    selected_agent: Literal["example_agent"],
    current_usage: Usage,
    total_usage: Usage,
) -> tuple[str, History, Usage, Usage]:
    """
    Process user message and generate response from the selected agent.
    
    This function orchestrates the flow of:
    1. Agent selection and dependency injection
    2. Tool registration for the agent
    3. Message processing with conversation history
    4. Usage tracking and state updates
    """
    agent = agents[selected_agent]
    agent_dependencies = AgentDependencies(current_user=current_user)

    # Register available tools for the agent
    tools = [create_draft_tool]
    register_tools(agent, tools)

    # Run agent with conversation history
    response = agent.run_sync(
        user_input,
        message_history=to_pydantic_history(history),
        deps=agent_dependencies,
    )
    
    assert response is not None, "Agent response should not be None"
    assert response.output is not None, "Agent response content should not be None"

    # Track API usage
    response_usage = response.usage()
    new_history = history + [
        ChatMessage(user_input, "user"),
        ChatMessage(response.output, "assistant"),
    ]
    
    current_usage.requests = response_usage.requests
    current_usage.request_tokens = response_usage.request_tokens
    current_usage.response_tokens = response_usage.response_tokens
    current_usage.total_tokens = response_usage.total_tokens
    total_usage.update(current_usage)

    return (
        "",  # Clear input box
        new_history,
        current_usage,
        total_usage,
    )


if __name__ == "__main__":
    demo = create_chat_ui(
        [],
        handle_user_message,  # type: ignore[call-arg]
        ["example_agent"],
    )
    demo.launch()
