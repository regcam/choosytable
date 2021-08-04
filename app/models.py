from flask_dance.consumer.storage import BaseStorage
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
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