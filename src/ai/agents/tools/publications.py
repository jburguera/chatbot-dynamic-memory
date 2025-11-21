from typing import Literal
from uuid import uuid4

from pydantic_ai import Agent, RunContext, Tool

from .. import AgentDependencies

PublicationPlatform = Literal["instagram", "linkedin", "twitter", "blog"]


async def create_draft(
    ctx: RunContext[AgentDependencies],
    platform: PublicationPlatform,
    content: str,
) -> dict[str, str]:
    """
    Generate a draft publication for a specified platform.
    
    This tool allows agents to create draft content optimized for different
    social media platforms or blog posts.

    Args:
        ctx: Runtime context with user dependencies
        platform: Target platform for the publication
        content: The content to be published
        
    Returns:
        Dictionary containing the publication URL for review
        
    Note:
        In production, this would integrate with actual platform APIs
        or a content management system.
    """
    # Placeholder implementation
    # In production, this would:
    # 1. Validate content for platform-specific requirements
    # 2. Store draft in database
    # 3. Return actual draft URL for user review
    
    draft_id = uuid4()
    return {
        "publication_url": f"https://example.com/draft/{draft_id}",
        "platform": platform,
        "status": "draft_created"
    }


# Define tool for Pydantic AI agent integration
create_draft_tool = Tool(
    name="create_draft",
    function=create_draft,
)


def register_tools(
    agent: Agent[AgentDependencies, str], 
    tools: list[Tool[AgentDependencies]]
) -> None:
    """
    Dynamically register tools for an agent instance.
    
    This helper function allows flexible tool registration, enabling different
    agents to have different capabilities based on their purpose.
    
    Args:
        agent: The agent instance to register tools for
        tools: List of Tool objects to register
        
    Note:
        Tools are refreshed on each agent run to ensure clean state
    """
    # Clear existing tools to avoid duplicates
    agent._function_tools.clear()

    # Register each tool with the agent
    for tool in tools:
        agent._register_tool(tool)
