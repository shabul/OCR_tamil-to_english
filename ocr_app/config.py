"""Application configuration values."""


class Config:
    """Base configuration shared across the app, Celery, and models."""

    # Core Flask config
    SECRET_KEY = 'tamil-ocr-solution'

    # MongoDB / GridFS
    MONGO_URL = 'mongodb://localhost:27017'
    MONGO_DATABASE = "tamil_ocr"
    MONGO_COLLECTION = "uploads"

    # Celery
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/tasks'
    CELERY_TASK_DEFAULT_QUEUE = 'tamil-ocr'

    # 3rd party integrations
    DETECT_LANGUAGE_API_KEY = "bbb385a240d1d4761d5acf77358ce7eb"
