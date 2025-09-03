from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL",
    )
    mongo_db_name: str = Field(
        default="story_tailer",
        description="MongoDB database name",
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host to bind the server to",
    )
    port: int = Field(
        default=8000,
        description="Port to bind the server to",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    base_files_dir: Path = Field(
        default=(Path(__file__).resolve().parent / "files"),
        description="Base directory for storing files",
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
