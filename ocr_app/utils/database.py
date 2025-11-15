"""MongoDB/GridFS helpers."""

import gridfs
from pymongo import MongoClient


def init_database(app):
    """Attach Mongo client, db, collection, and GridFS handles to the app."""
    client = MongoClient(app.config["MONGO_URL"])
    db = client[app.config["MONGO_DATABASE"]]
    collection = db[app.config["MONGO_COLLECTION"]]
    fs = gridfs.GridFS(db)

    app.mongo_client = client
    app.mongo_db = db
    app.mongo_collection = collection
    app.mongo_fs = fs

    return client, db, collection, fs
