import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4
from contextlib import suppress


class FileManager:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger(__name__)

    def store_image(self, raw_bytes: bytes, original_filename: Optional[str] = None) -> str:
        self._logger.info("Storing image...")

        extension = "png"

        if original_filename and "." in original_filename:
            extension = original_filename.rsplit(".", 1)[-1].lower()

        filename = f"{uuid4()}.{extension}"
        file_path = self._base_dir / "images" / filename

        with open(file_path, "wb") as file:
            file.write(raw_bytes)

        return f"images/{filename}"
    
    def store_audio(self, raw_bytes: bytes) -> str:
        self._logger.info("Storing audio...")

        extension = "wav"

        filename = f"{uuid4()}.{extension}"
        file_path = self._base_dir / "audio" / filename

        with open(file_path, "wb") as file:
            file.write(raw_bytes)

        return f"audio/{filename}"

    def resolve_path_from_url(self, url: str) -> Path:
        tail = url.replace("/files", "").lstrip("/")
        subdir, filename = tail.split("/", 1)
        return self._base_dir / subdir / filename

    def delete_story_files(self, story) -> None:
        if (url := story.image_url) is not None:
            self._delete_file(url)
        if (url := story.audio_url) is not None:
            self._delete_file(url)
    
    def _delete_file(self, file_url: str) -> None:
        path = self.resolve_path_from_url(file_url)

        with suppress(FileNotFoundError):
            path.unlink()
