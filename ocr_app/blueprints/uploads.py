"""Routes for upload lifecycle management."""

from bson.objectid import ObjectId
from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user, login_required
from pymodm.fields import File
from pymongo import DESCENDING

from ..models import User, UserUpload
from ..tasks.ocr import process_pdf

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.route("/uploads/<upload_id>")
@login_required
def uploads_status(upload_id):
    upload = UserUpload.get_by_id(ObjectId(upload_id))
    return jsonify(
        {
            "id": upload_id,
            "status": getattr(upload, "status", "Unknown"),
            "upload_time": getattr(upload, "upload_time", None),
            "done": getattr(upload, "done", False),
            "results": getattr(upload, "results", None),
        }
    )


@uploads_bp.route("/uploads")
@login_required
def uploads_list():
    uploads = {}
    for doc in UserUpload.objects.all().order_by([("upload_time", DESCENDING)]):
        upload_id = str(getattr(doc, "_id"))
        uploads[upload_id] = {
            "status": getattr(doc, "status", "Unknown"),
            "upload_time": getattr(doc, "upload_time", None),
            "done": getattr(doc, "done", False),
        }
    return jsonify(uploads)


@uploads_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    pdf_file = request.files.get("pdf")
    pdf_file = File(pdf_file, name=pdf_file.filename)

    user = User.get_by_id(current_user.email)
    user_upload = UserUpload(uploader=user, file_=pdf_file, status="uploaded")
    user_upload.save()

    async_result = process_pdf.apply_async([str(user_upload.get_id())])
    user_upload.task_id = str(async_result.task_id)
    user_upload.save()

    return jsonify({"upload_id": str(user_upload.get_id())})


@uploads_bp.route("/download/<upload_id>")
def download(upload_id):
    user_upload = UserUpload.get_by_id(ObjectId(upload_id))
    pdf_file = user_upload.file_
    file_content = pdf_file.read()
    response = make_response(file_content)
    response.headers.set("Content-Type", "application/pdf")
    response.headers.set("Content-Disposition", "attachment", filename=pdf_file.filename)
    return response


@uploads_bp.route("/viewPDF/<upload_id>")
def view_pdf(upload_id):
    user_upload = UserUpload.get_by_id(ObjectId(upload_id))
    pdf_file = user_upload.file_
    file_content = pdf_file.read()
    response = make_response(file_content)
    response.headers.set("Content-Type", "application/pdf")
    response.headers.set("Content-Disposition", "inline", filename=pdf_file.filename)
    return response


@uploads_bp.route("/uploads/updateText", methods=["POST"])
def update_text():
    payload = request.json
    upload_id = payload["upload_id"]
    page_no = payload["page_no"]
    edited_text = payload["edited_text"]
    user_upload = UserUpload.get_by_id(ObjectId(upload_id))
    user_upload.results[page_no]["editable_text"] = edited_text
    user_upload.save()
    return jsonify({"message": "updated successfully"}), 200
