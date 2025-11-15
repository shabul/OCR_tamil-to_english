"""Celery task that extracts text from uploaded PDFs."""

import re

from celery.exceptions import TaskError
from celery.utils.log import get_task_logger
from pdf2image import convert_from_bytes
import pytesseract

from ocr_app.extensions import celery
from ocr_app.models import UserUpload

logger = get_task_logger("process_pdf")


@celery.task(name="process_pdf")
def process_pdf(upload_id):
    logger.warning("Processing upload_id=%s", upload_id)
    upload = UserUpload.get_by_id(upload_id)

    if not upload:
        raise TaskError(f"Upload {upload_id} not found")

    upload.status = "Converting to images"
    upload.save()

    pdf_file = upload.file_
    images = convert_from_bytes(pdf_file.read(), fmt="jpeg")

    upload.status = "Processing"
    upload.save()

    results = []
    for image in images:
        extracted_text = pytesseract.image_to_string(image, lang="tam")
        extracted_text = extracted_text.replace("\n", " ")
        extracted_text = re.sub("[0-9]+", "", extracted_text)
        results.append({"extracted_text": extracted_text, "editable_text": extracted_text})

    upload.results = results
    upload.status = "Done"
    upload.done = True
    upload.save()
