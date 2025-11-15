"""Shared Flask extensions."""

from celery import Celery
from flask_login import LoginManager

login_manager = LoginManager()
celery = Celery("ocr_app")


def init_celery(app):
    """Bind Celery to the Flask app context."""
    celery.conf.update(app.config)

    class AppContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = AppContextTask

    # Import tasks so Celery registers them.
    from ocr_app.tasks import ocr  # noqa: F401

    return celery
