# Tamil OCR Service 
`[Authored : 2019 | Published 2025]`

Flask application that lets authenticated users upload Tamil PDF documents, runs OCR asynchronously through Celery/Tesseract, and lets users review, edit, and download the processed text.

## Features
- Email/password authentication powered by Flask-Login and MongoDB (via PyMODM).
- Upload PDFs that are stored in Mongo/GridFS and processed page-by-page by a Celery worker.
- OCR is performed with `pdf2image` + `pytesseract` (Tamil language data) and results are persisted for each page.
- Dashboard UI polls upload status (`/uploads` API), allows inline text edits, and supports download or inline preview of the original PDF.
- Configurable MongoDB/Redis endpoints and DetectLanguage API key via `ocr_app/config.py`.

## Project Structure
```
.
├── app.py                  # Flask entrypoint (used by Flask & Celery)
├── requirements.txt
├── ocr_app/
│   ├── __init__.py         # Application factory & blueprint registration
│   ├── config.py           # Centralized settings (Flask, Mongo, Celery, APIs)
│   ├── extensions.py       # Flask-Login + Celery instances
│   ├── models.py           # PyMODM models for users and uploads
│   ├── utils/
│   │   └── database.py     # Mongo/GridFS initialization helper
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── auth.py         # Signup/login/logout routes
│   │   ├── main.py         # Public pages (home, dashboard, profile)
│   │   └── uploads.py      # Upload lifecycle + JSON APIs
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── ocr.py          # `process_pdf` Celery task
│   ├── templates/          # Jinja templates (login, dashboard, etc.)
│   └── static/             # CSS/JS/asset files
└── …
```

## Prerequisites
1. **Python** 3.9+ and `pip`.
2. **MongoDB** running locally (defaults to `mongodb://localhost:27017`) or update `Config` values.
3. **Redis** running locally for Celery’s broker/result backend (defaults to `redis://localhost:6379/0`).
4. **Tesseract OCR** with the Tamil (`tam.traineddata`) language pack installed on the host system.
5. **Poppler** utilities (required by `pdf2image` for PDF rasterization).

On macOS you can install the native dependencies via Homebrew:
```bash
brew install tesseract poppler redis mongodb-community
# optional: brew install tesseract-lang    # installs extra traineddata files
```

## Setup
1. Create and activate a virtual environment, then install Python dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Ensure MongoDB and Redis are running, and the Tesseract + Poppler binaries are on your `PATH`.
3. (Optional) Update `ocr_app/config.py` if you need to change database URLs, Celery settings, or the DetectLanguage API key.
4. Export Flask environment variables for development:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```
5. Start the Flask dev server:
   ```bash
   flask run --host=0.0.0.0 --port=8080
   ```
6. In another terminal (same virtualenv), start the Celery worker so uploads are processed:
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

## Usage
1. Visit `http://localhost:8080`, create an account via the signup page, then log in.
2. Use the dashboard to upload a Tamil PDF. Each upload immediately creates a `UserUpload` document and enqueues a `process_pdf` Celery task.
3. The dashboard polls `/uploads` for status. Once finished you can:
   - View extracted text per page (and edit it inline, which calls `/uploads/updateText`).
   - Download or preview the original PDF (`/download/<id>` / `/viewPDF/<id>`).
4. Processed results are stored in MongoDB’s GridFS and can be retrieved later via the dashboard API.

## About Shabul
Built by Shabul to make Tamil OCR less painful. Say hey on [LinkedIn](https://www.linkedin.com/in/shabul/) or browse more projects at [shabul.github.io](https://shabul.github.io/). If this helps your workflow, toss a star or follow [@shabul](https://github.com/shabul) for more experiments.

## Notes
- All sensitive settings (DB URLs, API keys, queues) live in `ocr_app/config.py`; consider replacing the hard-coded values with environment variables before deploying.
- The Celery task currently extracts Tamil text; add translation or other post-processing inside `ocr_app/tasks/ocr.py` as needed.
- GridFS handles file storage transparently via PyMODM’s `FileField`, so no local file-system storage is required.
