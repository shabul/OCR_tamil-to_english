from pymodm import connect, fields, MongoModel
from flask_login import UserMixin

from .config import Config
from bson.objectid import ObjectId
from datetime import datetime

# Connect to MongoDB first. PyMODM supports all URI options supported by
# PyMongo. Make sure also to specify a database in the connection string:
connect("{mongo_url}/{database}".format(**{
    "mongo_url": Config.MONGO_URL,
    "database": Config.MONGO_DATABASE
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
            return None

    def get_id(self):
        return self.email

class UserUpload(MongoModel):
    uploader = fields.ReferenceField(User, on_delete=fields.ReferenceField.CASCADE)
    file_ = fields.FileField()
    status = fields.CharField()
    upload_time = fields.DateTimeField(default=datetime.utcnow)
    results = fields.ListField()
    done = fields.BooleanField(default=False)
    task_id = fields.CharField()

    @classmethod
    def get_by_id(cls, _id):
        try:
            object_id = _id if isinstance(_id, ObjectId) else ObjectId(_id)
            upload = cls.objects.get({'_id': object_id})
            return upload
        except cls.DoesNotExist:
            return None

    def get_id(self):
        return self._id
