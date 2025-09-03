from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient

from app.application import StoryApplication
from app.settings import Settings
from app.infrastructure import (
    MongoStoryRepository,
    StoryGenerator,
    StorySynthesizer,
    FileManager,
)


class ApplicationContainer(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)
    
    mongo_client: providers.Singleton[AsyncIOMotorClient] = providers.Singleton(
        AsyncIOMotorClient,
        settings.provided.mongo_url,
    )

    database = providers.Singleton(
        lambda client, db_name: client[db_name],
        mongo_client,
        settings.provided.mongo_db_name,
    )
    
    story_repository = providers.Singleton(
        MongoStoryRepository,
        db=database,
    )
    
    story_generator = providers.Singleton(StoryGenerator)
    file_manager = providers.Singleton(
        FileManager,
        base_dir=settings.provided.base_files_dir,
    )
    story_synthesizer = providers.Singleton(StorySynthesizer, file_manager=file_manager)

    application = providers.Factory(
        StoryApplication,
        story_repository=story_repository,
        generator=story_generator,
        synthesizer=story_synthesizer,
        file_manager=file_manager,
    )
