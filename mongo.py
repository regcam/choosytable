from flask import Flask, redirect, url_for, session, render_template, request, jsonify, g
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
import os
from flask_dance.contrib.google import make_google_blueprint, google
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
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
  else:
    session['resp']=google.get("/oauth2/v1/userinfo").json()

@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/welcome")
def home():
  e = ['Black', 'Latinx', 'Native American', 'Asian']
  x=star.find_one({'email':session['resp']['email']})
  if x is not None:
    return render_template(
      'person.html',
      personid=x['_id'],
      email=x['email'],
      name=x['name'],
      ethnicity=x['ethnicity'],
      e=e)
  else:
    return render_template(
      'person.html',
      email=session['resp']['email'],
      name=session['resp']['name'],
      e=e)

@app.route('/company', methods=['GET','POST','PUT'])
def company():
  if request.method == 'GET':
    companies=star.find({'reviews':{"$exists":True}})
    return render_template('company.html',companies=companies)
  elif request.method in ('POST', 'PUT'):
    company = request.json['company']
    creator = session['resp']['name']
    reviews = request.json['reviews']
    output={}
    try:
      return json_util.dumps(star.insert({'created' : datetime.now(), 'company': company, 'creator': creator, 'reviews': reviews}))
    except Exception as e:
      output = {'error' : str(e)}
      return jsonify(output)

@app.route('/company/<company_id>', methods=['GET','POST','PUT'])
def single_company(company_id):
  if request.method=='GET':
    return json_util.dumps(star.find_one({'_id': ObjectId(company_id)}))
  elif request.method in ('POST','PUT'):
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

@app.route('/person/<person_id>', methods=['GET','PUT','POST'])
def single_person(person_id):
  if request.method=='GET':
    try:
      return json_util.dumps(star.find_one({'_id': ObjectId(person_id)}))
    except:
      output = {'error' : 'person not found'}
      return jsonify(output)
  elif request.method in ('POST','PUT'):
    try:
      star.update(
        {'_id':ObjectId(person_id)},
        {
          '$set':{
          'name':request.form['name'],
          'ethnicity':request.form['ethnicity'],
          "last_modified":datetime.now()} 
        } 
      )
      output = {'message' : 'Your profile has been updated'}
      return jsonify({'result' : output})
    except Exception as e:
      output = {'error' : str(e)}
      return jsonify(output)

@app.route('/person', methods=['GET','POST','PUT'])
def person():
  if request.method=='GET':
    if request.args:
      name=request.args.get("name","")
      return json_util.dumps(star.find({"$and":[{'name':name},{'email':{"$exists":True}}]}))
    else:
      return json_util.dumps(star.find({'email':{"$exists":True}}))
  elif request.method in ('POST','PUT'):
    name = session['resp']['name']
    email = session['resp']['email']
    ethnicity = request.form['ethnicity']
    output={}
    try:
      return json_util.dumps(star.insert({'created':datetime.now(), 'name':name, 'email':email, 'ethnicity':ethnicity}))
    except Exception as e:
      output = {'error' : str(e)}
      return jsonify(output)

@app.route("/logout")
def logout():
    token = blueprint.token["access_token"]
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.ok, resp.text
    #logout_user()        # Delete Flask-Login's session cookie
    del blueprint.token  # Delete OAuth token from storage
    return render_template('bye.html')

if __name__ == '__main__':
    app.run(debug=True)