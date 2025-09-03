from pydantic import BaseModel, Field


class ImageInsights(BaseModel):
    title: str = Field(
        ...,
        description="A catchy, descriptive title for the story.",
    )
    caption: str = Field(
        ..., 
        description="A detailed description of the scene (no inventions).",
    )
    subjects: list[str] = Field(
        default_factory=list,
        description="Main visible entities as short noun phrases (e.g., 'old man', 'red bicycle')",
    )
    setting: str = Field(
        ...,
        description="Concise environment description (e.g., 'snowy forest at dusk').",
    )
    colors: list[str] = Field(
        default_factory=list,
        description="Dominant or notable colors/palettes (e.g., 'warm amber', 'cold blue-gray').",
    )
    time_of_day: str | None = Field(
        default=None,
        description="Time context if visible (e.g., 'dawn', 'noon', 'twilight', 'night').",
    )


class RestrictedContentResponse(BaseModel):
    summary: str | None = Field(
        default=None,
        description="One-sentence rationale grounded in visible/explicit cues.",
    )
    is_restricted: bool = Field(
        default=False,
        description="True if content should be blocked for under-18.",
    )


class StoryGenerationResponse(BaseModel):
    title: str = Field(..., description="The title of the story.")
    text: str = Field(..., description="The text of the story.")
