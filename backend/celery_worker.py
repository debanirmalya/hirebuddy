from celery import Celery
import os

def make_celery(app_name=__name__):
    """
    Creates and configures the Celery app instance.
    Defaults to Redis for both broker and backend.
    """
    celery = Celery(
        app_name,
        broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    )

    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )

    return celery


celery_app = make_celery("hire_buddy")

import tasks.parse_resume_llm
import tasks.generate_doc_request

if __name__ == "__main__":
    print("✅ Registered Celery tasks:")
    for task_name in celery_app.tasks.keys():
        print(f" - {task_name}")
