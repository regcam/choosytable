from flask import Flask, redirect, url_for, session, render_template, request, jsonify, g
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
import os
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.environ.get("SECRET_KEY")
app.config['GOOGLE_OAUTH_CLIENT_ID']=os.environ.get("GOOGLE_CLIENT_ID")
app.config['GOOGLE_OAUTH_CLIENT_SECRET']=os.environ.get("GOOGLE_CLIENT_SECRET")
blueprint = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(blueprint, url_prefix="/login")

mongo = PyMongo(app)
star = mongo.db.stars
db = mongo.db

@app.before_request
def before_request():
  if not google.authorized and "google" not in request.path:
    return render_template("index.html")

@app.route("/")
def home():
  resp = google.get("/oauth2/v1/userinfo")
  return render_template(
    'welcome.html', 
    email=resp.json()["email"], 
    database=str(db), 
    collection=str(star), 
    latestInfo=str(star.find_one()))

@app.route('/company', methods=['GET'])
def get_all_companies():
  return json_util.dumps(star.find({'reviews':{"$exists":True}}))

@app.route('/company', methods=['POST'])
def add_company():
  company = request.json['company']
  creator = request.json['creator']
  reviews = request.json['reviews']
  output={}
  try:
      return json_util.dumps(star.insert({'created' : datetime.now(), 'company': company, 'creator': creator, 'reviews': reviews}))
  except Exception as e:
      output = {'error' : str(e)}
      return jsonify(output)

@app.route('/company/<company_id>', methods=['GET'])
def get_company(company_id):
  return json_util.dumps(star.find_one({'_id': ObjectId(company_id)}))

@app.route('/company/<company_id>', methods=['POST'])
def update_company(company_id):
  r = star.find_one({'_id' : ObjectId(company_id)})
  if r:
    for key in request.json.keys():
        r[key] = request.json[key]
    try:
        output= star.replace_one({'_id' : ObjectId(company_id)}, r)
        output= star.update_one({'_id' : ObjectId(company_id)}, { "$set": {'last_modified':datetime.now() } } )
        output = {'message' : 'company updated'}
        return jsonify({'result' : output})
    except Exception as e:
        output = {'error' : str(e)}
        return jsonify(output)
  else:
    output = {'error' : 'company not found'}
    return jsonify(output)

@app.route('/person/<person_id>', methods=['GET'])
def get_person(person_id):
  return json_util.dumps(star.find_one({'_id': ObjectId(person_id)}))

@app.route('/person/<person_id>', methods=['POST'])
def update_person(person_id):
  r = star.find_one({'_id' : ObjectId(person_id)})
  if r:
    for key in request.json.keys():
        r[key] = request.json[key]
    try:
        output= star.replace_one({'_id' : ObjectId(person_id)}, r)
        output= star.update_one({'_id' : ObjectId(person_id)}, { "$set": {'last_modified':datetime.now() } } )
        output = {'message' : 'person updated'}
        return jsonify({'result' : output})
    except Exception as e:
        output = {'error' : str(e)}
        return jsonify(output)
  else:
    output = {'error' : 'person not found'}
    return jsonify(output)

@app.route('/person', methods=['GET'])
def get_all_persons():
  return json_util.dumps(star.find({'email':{"$exists":True}}))

@app.route('/person', methods=['POST'])
def add_person():
  name = request.json['name']
  email = request.json['email']
  ethnicity = request.json['ethnicity']
  output={}
  try:
      return json_util.dumps(star.insert({'created' : datetime.now(), 'name': name, 'email': email, 'ethnicity': ethnicity}))
  except Exception as e:
      output = {'error' : str(e)}
      return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)