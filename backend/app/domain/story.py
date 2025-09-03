from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class StoryFlavor(str, Enum):
    FAIRY_TALE = "fairy_tale"
    THRILLER = "thriller"
    ROMANCE = "romance"
    SCIENCE_FICTION = "science_fiction"


class StoryStatus(str, Enum):
    GENERATING_STORY = "generating_story"
    COMPLETED = "completed"
    GENERATING_AUDIO = "generating_audio"
    FAILED = "failed"
    AUDIO_TOO_LONG = "audio_too_long"
    RESTRICTED_CONTENT_DETECTED = "restricted_content_detected"
    JUST_CREATED = "just_created"


@dataclass
class Story:
    id: str
    flavor: StoryFlavor
    title: str
    story_text: str
    created_at: datetime
    status: StoryStatus = StoryStatus.GENERATING_STORY
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration_seconds: Optional[float] = None
    generation_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
