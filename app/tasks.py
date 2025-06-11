import time

from app.celery_app import celery_app

@celery_app.task
def debug_task(word: str):
    print(f"Debug task started for: {word}")
    time.sleep(5)  # Simulate a long-running task
    print(f"Debug task completed for: {word}")
    return {"status": "completed", "word": word} 