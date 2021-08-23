from flask import Flask, redirect, url_for, render_template, request, jsonify, flash
from flask_pymongo import PyMongo, ObjectId
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage import BaseStorage
from pymemcache.client.base import PooledClient
from bson import json_util
from flask_paginate import Pagination, get_page_args
from flask_navigation import Navigation

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'choosytable'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/choosytable'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.urandom(24).hex()
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID")
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get(
    "GOOGLE_CLIENT_SECRET")

# setup login manager
login_manager = LoginManager()
login_manager.login_view = "google.login"

blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    offline=True,
    reprompt_consent=True
    )
app.register_blueprint(blueprint, url_prefix="/login")

mongo = PyMongo(app)
ct = mongo.db.choosytable
nav = Navigation(app)

nav.Bar('top', [
    nav.Item('Home', 'person'),
    nav.Item('Companies', 'company'),
    nav.Item('People', 'person'),
    nav.Item('Logout', 'logout')
])

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

client = PooledClient('localhost', serde=JsonSerde())

from app.main import app as main_blueprint
app.register_blueprint(main_blueprint)

from app import models