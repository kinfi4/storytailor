import io
import logging

import wave
from piper import PiperVoice, SynthesisConfig

from app.domain import Story, StoryFlavor, StoryStatus

from ..file_manager import FileManager


class StorySynthesizer:
    MAX_AUDIO_DURATION_SECONDS = 4 * 60

    def __init__(self, file_manager: FileManager) -> None:
        self._voice = PiperVoice.load(model_path="/app/en_US-lessac-medium.onnx")

        self._config_for_flavor = {
            StoryFlavor.FAIRY_TALE: SynthesisConfig(length_scale=1.10, noise_scale=0.70, noise_w_scale=0.8, volume=1.0),
            StoryFlavor.ROMANCE: SynthesisConfig(length_scale=1.05, noise_scale=0.68, noise_w_scale=0.8, volume=0.95),
            StoryFlavor.SCIENCE_FICTION: SynthesisConfig(length_scale=0.98, noise_scale=0.62, noise_w_scale=0.7, volume=1.0),
            StoryFlavor.THRILLER: SynthesisConfig(length_scale=0.92, noise_scale=0.66, noise_w_scale=0.7, volume=1.05),
        }

        self._files = file_manager
        self._logger = logging.getLogger(__name__)

    async def synthesize_audio_for(self, story: Story) -> Story:
        self._logger.info(f"Synthesizing audio for story {story.title}...")

        config = self._config_for_flavor[story.flavor]

        with io.BytesIO() as buffer:
            # Provide a proper Wave_write for Piper
            with wave.open(buffer, "wb") as wav_writer:
                self._voice.synthesize_wav(
                    text=story.story_text,
                    wav_file=wav_writer,
                    syn_config=config,
                )

            audio_bytes = buffer.getvalue()

        audio_url = self._files.store_audio(audio_bytes)

        story.audio_url = audio_url

        story = self._check_audio_length(audio_bytes, story)

        return story
    
    def _calculate_duration_seconds(self, audio_bytes: bytes) -> float | None:
        with io.BytesIO(audio_bytes) as rb:
            with wave.open(rb, "rb") as wf:
                frames = wf.getnframes()
                framerate = wf.getframerate()
                return frames / float(framerate) if framerate else None

    def _check_audio_length(self, audio_bytes: bytes, story: Story) -> Story:
        story.audio_duration_seconds = self._calculate_duration_seconds(audio_bytes)
        
        if int(story.audio_duration_seconds or 0) > self.MAX_AUDIO_DURATION_SECONDS:
            story.status = StoryStatus.AUDIO_TOO_LONG
            story.error_message = f"Audio duration is too long. Maximum duration is {self.MAX_AUDIO_DURATION_SECONDS} seconds"
            return story
        
        story.status = StoryStatus.COMPLETED
        return story
