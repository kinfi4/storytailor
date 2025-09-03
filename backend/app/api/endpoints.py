from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Query, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse

from app.api.serializers import (
    StoryGenerationRequest,
    StoryGenerationResponse,
    StoryListResponse,
)
from app.application import StoryApplication
from app.infrastructure import FileManager
from app.containers import ApplicationContainer

router = APIRouter(prefix="/api", tags=["story-tailer"])


@router.post(
    "/stories/generate",
    response_model=StoryGenerationResponse,
)
@inject
async def generate_story(
    request_json: Annotated[str, Form(..., alias="request")],
    image: UploadFile = File(..., description="The image to generate a story from"),
    app: StoryApplication = Depends(Provide[ApplicationContainer.application]),
) -> StoryGenerationResponse:
    request = StoryGenerationRequest.model_validate_json(request_json)

    story = await app.initiate_story_generation(
        request=request,
        raw_image=await image.read(),
    )

    return StoryGenerationResponse.from_domain(story)


@router.get(
    "/stories/{story_id}",
    response_model=StoryGenerationResponse,
)
@inject
async def get_story(
    story_id: str,
    app: StoryApplication = Depends(Provide[ApplicationContainer.application]),
) -> StoryGenerationResponse:
    return StoryGenerationResponse.from_domain(
        story=await app.get_story_by_id(story_id),
    )


@router.get(
    "/stories",
    response_model=StoryListResponse,
)
@inject
async def list_stories(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    app: StoryApplication = Depends(Provide[ApplicationContainer.application]),
) -> StoryListResponse:
    stories, total = await app.list_stories(page=page, page_size=page_size)

    return StoryListResponse.from_domain(
        stories=stories,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete(
    "/stories/{story_id}",
    status_code=204,
)
@inject
async def delete_story(
    story_id: str,
    app: StoryApplication = Depends(Provide[ApplicationContainer.application]),
) -> None:
    await app.delete_story(story_id)


@router.get("/files/{filepath:path}")
@inject
async def get_file(
    filepath: str,
    file_manager: FileManager = Depends(Provide[ApplicationContainer.file_manager]),
):
    try:
        file_path = file_manager.resolve_path_from_url(f"/files/{filepath}")
    except ValueError:
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(str(file_path))
