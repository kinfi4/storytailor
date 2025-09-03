import os
import asyncio

from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

celery = Celery("story_tailer", broker=broker_url, backend=result_backend)
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    worker_hijack_root_logger=False,
)


@celery.task(name="tasks.generate_story")
def generate_story_task(story_id: str, request_json: dict) -> None:
    from app.containers import ApplicationContainer
    from app.api.serializers import StoryGenerationRequest

    app = ApplicationContainer().application()
    request = StoryGenerationRequest.model_validate(request_json)

    asyncio.run(app.perform_story_generation(story_id=story_id, request=request))
