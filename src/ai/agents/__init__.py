from pydantic import BaseModel, Field
from ...users.entities.user import CurrentUser


class AgentDependencies(BaseModel):
    """Agent dependencies inject in every call."""

    current_user: CurrentUser = Field(
        ...,
        description="User registry for storing and retrieving user information.",
    )
