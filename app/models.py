from flask_dance.consumer.storage import BaseStorage
from flask_login import UserMixin
from app import ct, login_manager
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime

class MongoStorage(BaseStorage):
    def __init__(self, email):
        super(MongoStorage, self).__init__()
        self.email = email

    def get(self, blueprint):
        u = ct.find_one({'email': self.email})
        if u is None:
            return None
        else:
            return u

    def set(self, blueprint, token):
        ct.update_one({'email': self.email},{'$set': {'token': token}})

    def delete(self, blueprint):
        ct.update(
            {'email': self.email}, 
            {'$pull': {'email': self.email}}
        )

class JsonSerde(object):
    def serialize(self, key, value):
        if isinstance(value, str):
            return value, 1
        return json_util.dumps(value), 2

    def deserialize(self, key, value, flags):
       if flags == 1:
           return value
       if flags == 2:
           return json_util.loads(value)
       raise Exception("Unknown serialization format")

class User(UserMixin):
    def __init__(self, email):
        self.email = email

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return str(self.email)

@login_manager.user_loader
def load_user(email):
    u = ct.find_one({'email': email})
    if not u:
        return False
    return User(u['email'])