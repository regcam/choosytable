from flask import Flask, redirect, url_for, render_template, request, jsonify, flash, current_app
from flask_pymongo import PyMongo, ObjectId
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage import BaseStorage
from pymemcache.client.base import PooledClient
from bson import json_util
from flask_paginate import Pagination, get_page_args
from flask_navigation import Navigation
from .constants import (
    ETHNICITY_OPTIONS as iel,
    GENDER_OPTIONS as igl, 
    POSITION_OPTIONS as p,
    AGE_OPTIONS as age,
    LOCATION_OPTIONS as location,
    HIGHLIGHTED_ETHNICITIES as e
)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME', 'choosytable')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/choosytable')
    
    # Security: Use environment variable for secret key to maintain sessions across restarts
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise ValueError(
            "SECRET_KEY environment variable must be set. "
            "Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
        )
    app.secret_key = secret_key
    
    # OAuth configuration
    app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID")
    app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    # Development OAuth settings - only set if explicitly enabled
    if os.environ.get('FLASK_ENV') == 'development':
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    
    return app

# Initialize global objects
mongo = None
ct = None 
nav = None
blueprint = None
login_manager = None
client = None

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

def init_app_components(app):
    """Initialize app components after app creation"""
    global mongo, ct, nav, blueprint, login_manager, client
    
    # MongoDB setup
    mongo = PyMongo(app)
    ct = mongo.db.choosytable
    
    # Check if we're in development mode with mock auth
    use_mock_auth = os.environ.get('USE_MOCK_AUTH', '').lower() == 'true'
    
    # Navigation setup  
    if use_mock_auth:
        nav = Navigation(app)
        nav.Bar('top', [
            nav.Item('Home', 'main.home'),
            nav.Item('Companies', 'main.company'),
            nav.Item('People', 'main.person'),
            nav.Item('Mock Login', 'mock_auth.mock_login'),
            nav.Item('Logout', 'main.logout')
        ])
    else:
        nav = Navigation(app)
        nav.Bar('top', [
            nav.Item('Home', 'main.home'),
            nav.Item('Companies', 'main.company'),
            nav.Item('People', 'main.person'),
            nav.Item('Logout', 'main.logout')
        ])
    
    # OAuth blueprint or mock auth
    if use_mock_auth:
        from app.mock_auth import mock_auth_bp
        app.register_blueprint(mock_auth_bp)
        blueprint = None  # No real OAuth blueprint needed
        print("\n🔧 DEVELOPMENT MODE: Using mock authentication")
        print("   Visit /mock/login to log in as test@example.com\n")
    else:
        # OAuth blueprint
        blueprint = make_google_blueprint(
            client_id=os.environ.get("GOOGLE_CLIENT_ID"),
            client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
            scope=["profile", "email"],
            offline=True,
            reprompt_consent=True
        )
        app.register_blueprint(blueprint, url_prefix="/login")
    
    # Login manager setup
    login_manager = LoginManager(app)
    if use_mock_auth:
        login_manager.login_view = "mock_auth.mock_login"
    else:
        login_manager.login_view = "google.login"
    
    # Cache client setup
    cache_host = os.environ.get('MEMCACHED_HOST', 'localhost')
    client = PooledClient(cache_host, serde=JsonSerde())
    
    # Register blueprints
    from app.main import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app

app = init_app_components(create_app())

# Import models after everything is set up
from . import models
