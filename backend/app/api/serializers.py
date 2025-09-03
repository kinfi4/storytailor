from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.domain.story import Story, StoryFlavor, StoryStatus


class StoryGenerationRequest(BaseModel):
    flavor: StoryFlavor
    additional_context: Optional[str] = Field(
        default=None,
        alias="additionalContext",
        description="Additional instructions or context for the story",
    )
    eighting_plus_enabled: bool = Field(
        default=False,
        alias="eightingPlusEnabled",
        description="Whether to allow 18+ content",
    )


class StoryGenerationResponse(BaseModel):
    id: str
    flavor: StoryFlavor
    title: str
    story_text: str = Field(..., alias="storyText")
    image_url: str | None = Field(None, alias="imageUrl")
    audio_url: str | None = Field(None, alias="audioUrl")
    audio_duration_seconds: float | None = Field(None, alias="audioDurationSeconds")
    generation_time_seconds: float | None = Field(None, alias="generationTimeSeconds")
    created_at: datetime = Field(..., alias="createdAt")
    status: StoryStatus = Field(
        ..., 
        description="e.g., generating_story, generating_audio, completed, failed",
    )

    model_config = {
        "populate_by_name": True
    }

    @classmethod
    def from_domain(cls, story: Story) -> "StoryGenerationResponse":
        return cls(
            id=story.id,
            flavor=story.flavor,
            title=story.title,
            storyText=story.story_text,
            imageUrl=story.image_url,
            audioUrl=story.audio_url,
            audioDurationSeconds=story.audio_duration_seconds,
            generationTimeSeconds=story.generation_time_seconds,
            createdAt=story.created_at,
            status=story.status,
        )


class StoryListItem(BaseModel):
    id: str
    flavor: StoryFlavor
    title: str
    story_preview: str = Field(
        ..., 
        description="first 100 characters",
    )
    audio_url: Optional[str] = None
    created_at: datetime
    status: str
    
    @classmethod
    def from_domain(cls, story: Story) -> "StoryListItem":
        story_preview = (
            story.story_text[:100] + "..." 
            if len(story.story_text) > 100 
            else story.story_text
        )
        return cls(
            id=story.id,
            flavor=story.flavor,
            title=story.title,
            story_preview=story_preview,
            audio_url=story.audio_url,
            created_at=story.created_at,
            status=story.status.value,
        )


class StoryListResponse(BaseModel):
    stories: List[StoryListItem]
    total: int
    page: int
    page_size: int
    
    @classmethod
    def from_domain(
        cls, 
        stories: List[Story], 
        total: int, 
        page: int, 
        page_size: int,
    ) -> "StoryListResponse":
        return cls(
            stories=[StoryListItem.from_domain(story) for story in stories],
            total=total,
            page=page,
            page_size=page_size,
        )


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    code: Optional[str] = None
