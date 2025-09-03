from contextlib import suppress
import logging
from datetime import datetime, timezone
from uuid import uuid4
from time import perf_counter

from app.domain import IStoryRepository, Story, StoryStatus
from app.api.serializers import StoryGenerationRequest
from app.infrastructure import StoryGenerator, StorySynthesizer, FileManager
from app.exceptions import ResourceNotFound, RestrictedContentDetected


class StoryApplication:
    def __init__(
        self,
        story_repository: IStoryRepository,
        generator: StoryGenerator, 
        synthesizer: StorySynthesizer, 
        file_manager: FileManager,
    ) -> None:
        self.story_repository = story_repository
        self._generator = generator
        self._synthesizer = synthesizer
        self._files = file_manager

        self._logger = logging.getLogger(__name__)
    
    async def initiate_story_generation(self, request: StoryGenerationRequest, raw_image: bytes) -> Story:
        image_url = self._files.store_image(raw_image)

        story = Story(
            id=str(uuid4()),
            flavor=request.flavor,
            title="Story generation in progress...",
            story_text="Your story is generating, please wait a moment...",
            created_at=datetime.now(tz=timezone.utc),
            status=StoryStatus.JUST_CREATED,
            image_url=image_url,
        )

        await self.story_repository.save(story)

        try:
            from app.celery_app import celery

            celery.send_task(
                "tasks.generate_story",
                args=[story.id, request.model_dump(mode="json", by_alias=True)],
            )
        except Exception as e:
            self._logger.error(f"Failed to enqueue Celery task: {e}")

        return story

    async def perform_story_generation(self, story_id: str, request: StoryGenerationRequest) -> None:
        start_time = perf_counter()

        story = await self.get_story_by_id(story_id)

        try:
            await self._generate_story_text(story, request)
            await self._synthesize_audio(story)

            elapsed_seconds = perf_counter() - start_time
            story.generation_time_seconds = elapsed_seconds
            await self.story_repository.save(story)
        except Exception as exc:
            await self._make_story_failed(story, exc)

    async def get_story_by_id(self, story_id: str) -> Story:
        if (story := await self.story_repository.get_by_id(story_id)) is None:
            raise ResourceNotFound(f"Story with id '{story_id}' not found")

        return story

    async def list_stories(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Story], int]:
        return await self.story_repository.list_stories(page, page_size)

    async def delete_story(self, story_id: str) -> None:
        try:
            with suppress(ResourceNotFound):
                story = await self.get_story_by_id(story_id)
                self._files.delete_story_files(story)
        finally:
            await self.story_repository.delete(story_id)
    
    async def _synthesize_audio(self, story: Story) -> None:
        story = await self._synthesizer.synthesize_audio_for(story)
        await self.story_repository.save(story)

    async def _generate_story_text(self, story: Story, request: StoryGenerationRequest) -> None:
        story.status = StoryStatus.GENERATING_STORY
        await self.story_repository.save(story)

        file_path = self._files.resolve_path_from_url(story.image_url or "")
        with open(file_path, "rb") as img_file:
            raw_image = img_file.read()

        generated = await self._generator.generate(request, raw_image)

        story.title = generated.title
        story.story_text = generated.text
        story.status = StoryStatus.GENERATING_AUDIO

        await self.story_repository.save(story)

    async def _make_story_failed(self, story: Story, exc: Exception) -> None:

        if isinstance(exc, RestrictedContentDetected):
            self._logger.warning(f"Restricted content detected: `{exc}`")
            story.title = "Restricted content detected"
            story.story_text = (
                "This request was flagged as restricted for under-18 viewers. "
                "Enable 18+ content or provide a different image/context.\n\n"
                f"{str(exc)}"
            )
            story.status = StoryStatus.RESTRICTED_CONTENT_DETECTED
        else:
            self._logger.error(f"Failed to generate story: `{exc}`", exc_info=True)

            story.title = "Failed to generate story :("
            story.story_text = str(exc)
            story.status = StoryStatus.FAILED

        await self.story_repository.save(story)
