from abc import ABC, abstractmethod

from .story import Story


class IStoryRepository(ABC):
    @abstractmethod
    async def save(self, story: Story) -> None:
        pass
    
    @abstractmethod
    async def get_by_id(self, story_id: str) -> Story | None:
        pass
    
    @abstractmethod
    async def list_stories(
        self, 
        page: int = 1, 
        page_size: int = 10,
    ) -> tuple[list[Story], int]:
        pass

    @abstractmethod
    async def delete(self, story_id: str) -> None:
        pass
