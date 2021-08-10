from flask import Flask, redirect, url_for, render_template, request, jsonify, flash
from flask_pymongo import PyMongo, ObjectId
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage import BaseStorage

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

from app.main import bp as main_blueprint
app.register_blueprint(main_blueprint)