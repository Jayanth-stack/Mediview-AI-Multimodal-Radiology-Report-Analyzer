from __future__ import annotations

import os
from celery import Celery


BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "mediviewai",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

celery_app.conf.task_queues = {"analyze"}
celery_app.conf.task_default_queue = "analyze"
celery_app.conf.task_default_exchange = "analyze"
celery_app.conf.task_default_routing_key = "analyze"

