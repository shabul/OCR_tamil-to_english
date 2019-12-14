# Mongo db config
MONGO_URL = 'mongodb://localhost:27017'
MONGO_DATABASE = "tamil_ocr_dev"
MONGO_COLLECTION = "uploads"

# Secret key
SECRET_KEY = 'tamil-ocr-solution-dev'

# Celery config
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/dev_tasks'
CELERY_TASK_DEFAULT_QUEUE = 'tamil-ocr-dev'