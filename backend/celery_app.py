from celery import Celery
from config import settings

# Initialize Celery
celery_app = Celery(
    "mixmaster",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks.audio_processor"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.PROCESSING_TIMEOUT,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
)
