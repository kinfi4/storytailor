from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain import IStoryRepository, Story, StoryFlavor, StoryStatus


class MongoStoryRepository(IStoryRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = db.stories
    
    async def save(self, story: Story) -> None:
        story_dict = {
            "id": story.id,
            "flavor": story.flavor.value,
            "title": story.title,
            "story_text": story.story_text,
            "created_at": story.created_at,
            "status": story.status.value,
            "image_url": story.image_url,
            "audio_url": story.audio_url,
            "audio_duration_seconds": story.audio_duration_seconds,
            "generation_time_seconds": story.generation_time_seconds,
            "error_message": story.error_message,
        }

        await self.collection.replace_one(
            {"id": story.id}, 
            story_dict, 
            upsert=True,
        )
    
    async def get_by_id(self, story_id: str) -> Story | None:
        if (document := await self.collection.find_one({"id": story_id})) is None:
            return None
        
        return self._document_to_story(document)

    async def delete(self, story_id: str) -> None:
        await self.collection.delete_one({"id": story_id})

    async def list_stories(
        self, 
        page: int = 1, 
        page_size: int = 10,
    ) -> tuple[list[Story], int]:
        skip = (page - 1) * page_size
        
        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(page_size)
        stories: list[Story] = []

        async for document in cursor:
            stories.append(self._document_to_story(document))
        
        total = await self.collection.count_documents({})

        return stories, total
    
    def _document_to_story(self, document: dict) -> Story:
        return Story(
            id=document["id"],
            flavor=StoryFlavor(document["flavor"]),
            title=document.get("title", ""),
            story_text=document["story_text"],
            created_at=document["created_at"],
            status=StoryStatus(document["status"]),
            image_url=document.get("image_url"),
            audio_url=document.get("audio_url"),
            audio_duration_seconds=document.get("audio_duration_seconds"),
            generation_time_seconds=document.get("generation_time_seconds"),
            error_message=document.get("error_message"),
        )
