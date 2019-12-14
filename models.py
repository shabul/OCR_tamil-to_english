
from pymongo import TEXT
from pymongo.operations import IndexModel
from pymodm import connect, fields, MongoModel, EmbeddedMongoModel
from pymodm.manager import Manager
from flask_login import UserMixin

from config import MONGO_URL, MONGO_DATABASE
from bson.objectid import ObjectId
from datetime import datetime

# Connect to MongoDB first. PyMODM supports all URI options supported by
# PyMongo. Make sure also to specify a database in the connection string:


connect("{mongo_url}/{database}".format(**{
    "mongo_url": MONGO_URL,
    "database": MONGO_DATABASE
}))

class User(MongoModel, UserMixin):
    email = fields.EmailField(primary_key=True)
    fname = fields.CharField()
    lname = fields.CharField()
    password = fields.CharField()
    uploads = fields.ListField()

    @classmethod
    def get_by_id(cls, _id):
        try:
            user = cls.objects.get({'_id': _id})
            return user
        except cls.DoesNotExist:
            return {}

    def is_authenticated(self):
        return self.is_authenticated

    def get_id(self):
        return self.email

class UserUpload(MongoModel):
    uploader = fields.ReferenceField(User, on_delete=fields.ReferenceField.CASCADE)
    file_ = fields.FileField()
    status = fields.CharField()
    upload_time = fields.DateTimeField(default=datetime.now())
    results = fields.ListField()
    done = fields.BooleanField(default=False)
    task_id = fields.CharField()

    @classmethod
    def get_by_id(cls, _id):
        try:
            upload = cls.objects.get({'_id': ObjectId(_id)})
            return upload
        except cls.DoesNotExist:
            return {}

    def get_id(self):
        return self._id