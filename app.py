from flask import Flask, request, jsonify, redirect, render_template, make_response
import os
from pdf2image import convert_from_bytes
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import detectlanguage
from googletrans import Translator
from pymongo import MongoClient
from celery import Celery
from bson.objectid import ObjectId
from time import sleep
import gridfs
import json
import re
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User, UserUpload
from werkzeug.security import generate_password_hash, check_password_hash
from celery.exceptions import TaskError
from celery.utils.log import get_task_logger
from pymodm.fields import File
from pymongo import DESCENDING

app = Flask(__name__)
app.config.from_pyfile('config.py')
# print(app.config)

logger = get_task_logger("process_pdf")

# blueprint for auth routes in our app
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from main import main as main_blueprint
app.register_blueprint(main_blueprint)

# Init login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

detectlanguage.configuration.api_key = "bbb385a240d1d4761d5acf77358ce7eb"

def init_database(config):
    # Init database client
    client = MongoClient(config.get("MONGO_URL"))
    db = client[config.get("MONGO_DATABASE")]
    collection = db[config.get("MONGO_COLLECTION")]
    # File Storage
    fs = gridfs.GridFS(db)

    return client, db, collection, fs

# Init Database
client, db, uploads, fs = init_database(app.config)

# Initialize celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

current_dir = os.path.dirname(os.path.realpath(__file__))
temp_dir = os.path.join(current_dir, 'temp')

@celery.task(name="process_pdf")
def process_pdf(upload_id):

    from models import UserUpload

    logger.warning("upload_id" + upload_id)
    upload = UserUpload.get_by_id(upload_id)

    logger.warning(upload)

    if not upload:
        raise TaskError()

#   Update status to processing
    upload.status = "Converting to images"
    upload.save()

    pdf_file = upload.file_
    images = convert_from_bytes(pdf_file.read(), fmt='jpeg')
    
    upload.status = "Processing"
    upload.save()

    translator = Translator()

    results = []
    for image in images:
        result = {}
        extracted_text = pytesseract.image_to_string(image, lang="tam")  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
        extracted_text = extracted_text.replace("\n", " ")
        extracted_text = re.sub("[0-9]+", "", extracted_text)
        result["extracted_text"] = extracted_text
        result["editable_text"] = extracted_text
        # sleep(1)
        # try:
        #     translated_text = translator.translate([ extracted_text ])
        #     translated_text = translated_text[0].text
        # except json.decoder.JSONDecodeError:
        #     translated_text = "Unable to translate"
        # result["translated_text"] = translated_text
        results.append(result)
    
    # upload.status = "Translating to english"
    upload.save()
    
    upload.results = results

    upload.status = "Done"
    upload.done = True
    upload.save()

@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/uploads/<upload_id>")
@login_required
def uploads_status(upload_id):
    upload = UserUpload.get_by_id(ObjectId(upload_id))
    return jsonify(
        {
            "id": upload_id,
            "status": getattr(upload, "status", "Unknown"),
            "upload_time": getattr(upload, "upload_time", None),
            "done": getattr(upload, "done", False),
            "results": getattr(upload, "results", None)
        }
    )

@app.route("/uploads")
@login_required
def uploads_list():
    uploads = {}
    for doc in UserUpload.objects.all().order_by([('upload_time', DESCENDING )]):
        upload_id = str(getattr(doc, "_id"))
        uploads[upload_id] = {
            "status": getattr(doc, "status", "Unknown"),
            "upload_time": getattr(doc, "upload_time", None),
            "done": getattr(doc, "done", False),
        }
    return jsonify(uploads)


@app.route("/upload", methods=["POST"])
@login_required
def upload():

    # Get pdf file from Form
    pdf_file = request.files.get('pdf')

    pdf_file = File(pdf_file, name=pdf_file.filename)

    # Get user object
    user = User.get_by_id(current_user.email)
    
    user_upload = UserUpload(uploader = user, file_ = pdf_file, status="uploaded")

    user_upload.save()

    r = process_pdf.apply_async([str(user_upload.get_id())])
    task_id = r.task_id

    user_upload.task_id = str(task_id)
    user_upload.save()

    return jsonify({"upload_id": str(user_upload.get_id())})

@app.route('/download/<upload_id>')
def download(upload_id):
    user_upload = UserUpload.get_by_id(ObjectId(upload_id))
    pdf_file = user_upload.file_
    file_content = pdf_file.read()
    response = make_response(file_content)
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set(
        'Content-Disposition', 'attachment', filename=pdf_file.filename)
    return response


@app.route('/viewPDF/<upload_id>')
def view_pdf(upload_id):
    user_upload = UserUpload.get_by_id(ObjectId(upload_id))
    pdf_file = user_upload.file_
    file_content = pdf_file.read()
    response = make_response(file_content)
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set(
        'Content-Disposition', 'inline', filename=pdf_file.filename)
    return response


@app.route('/uploads/updateText', methods=['POST'])
def update_text():
    payload = request.json
    upload_id = payload['upload_id']
    page_no = payload['page_no']
    edited_text = payload['edited_text']
    user_upload = UserUpload.get_by_id(ObjectId(upload_id))
    user_upload.results[page_no]['editable_text'] = edited_text
    user_upload.save()
    return jsonify({
        "message": "updated successfully"
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
