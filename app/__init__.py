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

e = ['Black', 'Afro-Latino', 'Bahamian', 'Jamaican', 'African']
iel = ['White','Asian','Latino','Black','Afro-Latino',
'African','Indigenous People','Pacific Islander', 'Unspecified']
igl = ['Female','Male','Transgender','Agender','Unspecified']
p = [('software_engineer','Software Engineer'),('staff_engineer','Staff Engineer'),('lead_engineering','Lead Engineer'),
('architect','Architect'),('software_engineer_mngr','Software Engineer Manager'),('technical_mngr','Technical Manager'),('technical_drtr','Technical Director'),
('vp','VP'),('cto','CTO'),('network_engineer','Network Engineer'),('principal_architect','Principal Architect'),('qa_engineer','QA Engineer'),('sre','SRE'),('sdet','SDET'),
('project_mngr','Project Manager'),('program_mngr','Program Manager'),('devops_engineer','DevOps Engineer'),('systems_admin','Systems Admin'),
('dba','DBA'),('operations_engineer','Operations Engineer')]
age = ['18-24','25-34','35-44','45-54','55-64','65-74','75+']
location = ['AK','AL','AR','AS','AZ','CA''CO','CT','DC','DE',
'FL','GA','GU','HI','IA','ID','IL','IN','KS','KY','LA','MA',
'MD','ME','MI','MN','MO','MP','MS','MT','NC','ND','NE','NH','NJ',
'NM','NV','NY','OH','OK','OR','PA','PR','RI','SC','SD','TN',
'TX','UT','VA','VI','VT','WA','WI','WV','WY']

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
    nav.Item('Home', 'main.person'),
    nav.Item('Companies', 'main.company'),
    nav.Item('People', 'main.person'),
    nav.Item('Logout', 'main.logout')
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

from app.main import bp as main_blueprint
app.register_blueprint(main_blueprint)

from . import models