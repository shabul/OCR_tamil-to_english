"""Application entrypoint for the Tamil OCR service."""

from ocr_app import create_app
from ocr_app.extensions import celery, init_celery

app = create_app()
init_celery(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
