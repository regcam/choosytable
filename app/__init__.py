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

from app.main import bp as main_blueprint
app.register_blueprint(main_blueprint)

def get_css_framework():
    return app.config.get("CSS_FRAMEWORK", "bootstrap4")


def get_link_size():
    return app.config.get("LINK_SIZE", "sm")


def get_alignment():
    return app.config.get("LINK_ALIGNMENT", "")


def show_single_page_or_not():
    return app.config.get("SHOW_SINGLE_PAGE", True)

def find_creatorreviews(y):
    key=str(y['_id'])+"_reviews"
    querykey=client.get(key)
    if querykey == None:
        querykey=list(ct.find({'reviews.user': str(y['_id'])},{'reviews':1,'_id':1,'company':1}).sort('last_modified',-1))
        client.set(key, querykey)
    return querykey


def find_email(z):
    querykey=client.get(z)
    if querykey == None:
        querykey=ct.find_one({'email': z})
        client.set(z,querykey)
    return querykey


def get_pagination(**kwargs):
    kwargs.setdefault("record_name", "records")
    return Pagination(
        css_framework=get_css_framework(),
        link_size=get_link_size(),
        alignment=get_alignment(),
        show_single_page=show_single_page_or_not(),
        **kwargs
    )


def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return False

    info = resp.json()

    # Find this OAuth token in the database, or create it
    try:
        oauth = find_email(info['email'])
    except:
        print("User not found")
    else:
        oauth = info | token
        ct.insert(oauth)

    login_user(User(oauth['email']))

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


def find_reviews():
    z="find_reviews"
    querykey=client.get(z)
    if querykey == None:
        querykey=list(ct.find({'reviews': {"$exists": True}}).sort('last_modified',-1))
        client.set(z, querykey)
    return querykey


def findone_company(c):
    querykey=client.get(c)
    if querykey == None:
        querykey=ct.find_one({'_id': ObjectId(c)})
        client.set(c,querykey)
    return querykey

def pd_interviews(p,singlecompany):
    querykey=client.get(str(singlecompany['_id'])+"_pd_interviews")
    if querykey == None:
        winDict=[]
        wintype={}
        for j in p:
            if j[0] in singlecompany:
                df=pd.DataFrame(singlecompany[j[0]])
                grouped=df.groupby('user_ethnicity')

                for key,value in grouped:
                    for i in ['y','n','o']:
                        wintype[i]=int(((value['win']==i).sum()/len(grouped.apply(lambda x: x[x['user_ethnicity']==key]).index))*100)

                    winDict.append([j[1],key,wintype.copy()])
                    wintype.clear()
        querykey=winDict
        client.set(str(singlecompany['_id'])+"_pd_interviews",querykey)
    return querykey

from app import models