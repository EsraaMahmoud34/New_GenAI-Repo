from typing import Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langgraph.graph.message import add_messages


class UserProfile(BaseModel):
    skin_type: str | None = Field(
        default=None,
        description="The user's skin type: oily, dry, combination, or normal. Return null if not mentioned."
    )

    concerns: list[str] = Field(
        default_factory=list,
        description="The user's skincare concerns. Return an empty list [] if not mentioned. Never return null."
    )

    budget: float | None = Field(
        default=None,
        description="The user's maximum skincare budget. Return null if not mentioned."
    )

    preferences: list[str] = Field(
        default_factory=list,
        description="The user's skincare product preferences. Return an empty list [] if not mentioned. Never return null."
    )

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

    skin_type: str | None
    concerns: list[str]
    budget: float | None
    preferences: list[str]

