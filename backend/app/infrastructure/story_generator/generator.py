import base64
import logging
import os
from io import BytesIO
from typing import cast

from langchain_ollama import ChatOllama
from PIL import Image

from app.api.serializers import StoryGenerationRequest
from app.exceptions import RestrictedContentDetected

from .response_models import ImageInsights, StoryGenerationResponse, RestrictedContentResponse
from ..story_synthesizer.constants import flavour_to_wpm

# VLM (Qwen2.5-VL-7B) https://huggingface.co/spaces/opencompass/open_vlm_leaderboard, https://arxiv.org/html/2501.00321v2
# LLM (Qwen2.5-7B) 


class StoryGenerator:
    def __init__(self) -> None:
        self._vision_model_name = os.getenv("OLLAMA_VLM_MODEL", "qwen2.5vl:7b")
        self._txt_model_name = os.getenv("OLLAMA_TXT_MODEL", "qwen2.5:7b")
        self._ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")

        self._logger = logging.getLogger(__name__)

    async def generate(
        self,
        request: StoryGenerationRequest,
        image_bytes: bytes,
    ) -> StoryGenerationResponse:
        image_bytes = self._convert_image_to_jpeg(image_bytes)

        if not request.eighting_plus_enabled:
            await self._perform_elder_content_check(request, image_bytes)
        
        insights = await self._get_image_insights(request, image_bytes)

        self._logger.info("Got image insights: %s", insights)

        return await self._generate_story(request, insights)
    
    async def _perform_elder_content_check(
        self,
        request: StoryGenerationRequest,
        image_bytes: bytes,
    ) -> None:
        self._logger.info("Performing elder content check...")

        img_bytes_url: str = self._image_to_data_url(image_bytes)

        system = (
            "You are a concise content safety classifier."
            " Block explicit sexual content (nudity/acts/exploitation), graphic violence/gore,"
            " sexualization of minors, or hateful/terrorist propaganda."
            " Allow 16+ content: mild romance/affection, non-graphic injuries, sports, everyday scenes."
            " Decisions must be grounded strictly in the visible image and the user's extra text."
            " Output a compact JSON object only."
        )
        user = (
            "Classify if the content should be restricted for under-18 viewers."
            " Consider the image and this extra text (may be empty):\n\n"
            f"Extra instructions from the user: ```{request.additional_context}```\n\n"
            " Keep summary one sentence, grounded in visible cues."
        )
        messages = [
            {"role": "system", "content": [{"type": "text", "text": system}]},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user},
                    {"type": "image_url", "image_url": img_bytes_url},
                ],
            },
        ]

        structured = (
            ChatOllama(
                model=self._vision_model_name,
                base_url=self._ollama_url,
                temperature=0,
                num_ctx=2048,
            )
            .with_structured_output(RestrictedContentResponse)
        )

        result = cast(RestrictedContentResponse, await structured.ainvoke(messages))

        if result.is_restricted:
            raise RestrictedContentDetected(result.summary)

    async def _get_image_insights(self, request: StoryGenerationRequest, image_bytes: bytes) -> ImageInsights:
        self._logger.info("Getting image insights...")

        img_bytes_url: str = self._image_to_data_url(image_bytes)

        system = (
            "You are a meticulous vision assistant extracting grounded story-building cues."
            " Be literal and faithful to the image; do not invent entities or text."
            " Prefer short noun phrases. Avoid duplication across lists."
            " Output only JSON that matches the schema precisely."
        )
        user = (
            "Extract comprehensive grounded insights for story writing from the image."
            " Fill the schema thoroughly."
            " Use short, concrete phrases. Keep punctuation minimal."
            " Consider the user's extra instructions for context: "
            f"```{request.additional_context}```"
        )
        messages = [
            {"role": "system", "content": [{"type": "text", "text": system}]},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user},
                    {"type": "image_url", "image_url": img_bytes_url},
                ],
            },
        ]
        structured = (
            ChatOllama(
                model=self._vision_model_name,
                base_url=self._ollama_url,
                temperature=0.3,
                num_ctx=2048,
            )
            .with_structured_output(ImageInsights)
        )

        return cast(ImageInsights, await structured.ainvoke(messages))

    async def _generate_story(
        self,
        request: StoryGenerationRequest,
        insights: ImageInsights,
    ) -> StoryGenerationResponse:
        wpm = flavour_to_wpm[request.flavor]
        minutes = 4.0
        speech_margin = 0.92  # need this for pauses and extra effects
        max_words = int(wpm * minutes * speech_margin)

        tokens_to_predict = max(256, min(1024, int(max_words * 1.3)))

        if request.eighting_plus_enabled:
            content_guideline = (
                "18+ is enabled: mature themes are permitted. Do NOT depict minors, "
                "illegal or non-consensual acts. Avoid pornographic detail; be tasteful."
            )
        else:
            content_guideline = (
                "18+ is NOT enabled: content must be suitable for under-18. 16+ content is allowed. "
                "No explicit sexual content; no graphic violence/gore."
            )

        system = (
            "You are a seasoned storyteller. Write vivid, coherent prose tailored to the requested flavor."
            " Keep language accessible and engaging. "
            " Use natural rhythm for spoken delivery: short to medium sentences, varied cadence."
            " Format the story with clear paragraph breaks (one blank line between paragraphs)."
            " For major shifts in scene or time, insert a line with '---' as a break."
            f"{content_guideline}"
            " Output only the final story text; do not include a title or any commentary."
        )
        flavor_line = f"Flavor: {request.flavor.value}."
        context_line = f"Additional instructions for the story: {request.additional_context}"
        insight_brief = (
            "Use the following details as inspiration for your story, but feel free to creatively expand, add new elements, or imagine additional context to make the story more engaging and vivid:\n"
            + insights.model_dump_json(indent=2) + "\n"
        )
        user = (
            f"Write a story. The story text should be medium-large: at least 300 words, but less than the {max_words} words.\n"
            f"{flavor_line}\n\n"
            f"{insight_brief}\n"
            f"{context_line}"
        )

        messages = [
            {"role": "system", "content": [{"type": "text", "text": system}]},
            {"role": "user", "content": [{"type": "text", "text": user}]},
        ]

        llm = ChatOllama(
            model=self._txt_model_name,
            base_url=self._ollama_url,
            temperature=1.2,
            num_ctx=2048,
            num_predict=tokens_to_predict,
        )
        
        story_text = (await llm.ainvoke(messages)).content

        return StoryGenerationResponse(title=insights.title, text=str(story_text))

    @staticmethod
    def _image_to_data_url(image_bytes: bytes, mime: str = "image/jpeg") -> str:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime};base64,{b64}"
    
    def _convert_image_to_jpeg(self, image_bytes: bytes) -> bytes:
        with BytesIO(image_bytes) as input_buffer, BytesIO() as output_buffer:
            image = Image.open(input_buffer).convert("RGB")
            image.thumbnail((768, 768), Image.Resampling.LANCZOS)
            image.save(output_buffer, format="JPEG", quality=70, subsampling=2, optimize=True)

            return output_buffer.getvalue()
