import os
from celery import Celery

celery_app = Celery(
    "ingest",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
)

celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
