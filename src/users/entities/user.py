from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# Define allowed sectors for user classification
Sector = Literal[
    "technology",
    "healthcare",
    "finance",
    "education",
    "marketing",
    "other",
]

# Define allowed professions for user classification
Profession = Literal[
    "developer",
    "designer",
    "manager",
    "analyst",
    "writer",
    "consultant",
    "other",
]

# Define supported languages
Language = Literal[
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "de",  # German
    "pt",  # Portuguese
]


class CurrentUser(BaseModel):
    """
    User entity representing the current authenticated user.
    
    This model stores essential user information used for personalizing
    agent interactions and managing memory isolation.
    
    Attributes:
        id: Unique identifier for the user (UUID)
        name: Display name of the user
        sector: Primary industry or sector
        profession: Job role or professional category
        language: Preferred communication language (ISO 639-1 code)
    """

    id: UUID = Field(
        ...,
        description="Unique identifier for the user.",
    )
    
    name: str = Field(
        ...,
        description="Display name of the user.",
        max_length=100,
    )
    
    sector: Sector = Field(
        ...,
        description="Primary industry or sector of the user.",
    )
    
    profession: Profession = Field(
        ...,
        description="Job role or professional category.",
    )
    
    language: Language = Field(
        ...,
        description="Preferred language for communication (ISO 639-1 code).",
        max_length=10,
    )
