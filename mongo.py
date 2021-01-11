from flask import Flask, redirect, url_for, session
from flask_oauth import OAuth
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
import urllib.request,urllib.parse,urllib.error


# This is one of the Redirect URIs from Google APIs console
REDIRECT_URI = '/oauth2callback'

# Add your SECRET_KEY here
# Set your secret key as an evironment variable and use it as below
SECRET_KEY = ""
DEBUG = True

app = Flask(__name__)

# Your GOOGLE_CLIENT_ID and GOOGLE_CLIENT SECRET are needed here
# You can get them at https://code.google.com/apis/console
GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'
app.secret_key = SECRET_KEY
oauth = OAuth()

mongo = PyMongo(app)
star = mongo.db.stars
db = mongo.db

google = oauth.remote_app('google',
base_url='https://www.google.com/accounts/',
authorize_url='https://accounts.google.com/o/oauth2/auth',
request_token_url=None,
request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
'response_type': 'code'},
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_method='POST',
access_token_params={'grant_type': 'authorization_code'},
consumer_key=GOOGLE_CLIENT_ID,
consumer_secret=GOOGLE_CLIENT_SECRET)

@app.route("/")
def home():
  access_token = session.get('access_token')
  if access_token is None:
      return redirect(url_for('login'))
  
  access_token = access_token[0]

  headers = {'Authorization': 'OAuth '+access_token}
  req = urllib.request.Request('https://www.googleapis.com/oauth2/v1/userinfo',
                None, headers)
  try:
    res = urllib.request.urlopen(req)
  except urllib.error.HTTPError as e:
    if e.code == 401:
        # Unauthorized - bad token
        session.pop('access_token', None)
        return redirect(url_for('login'))
    return res.read()

@app.route('/welcome')
def welcome():
  html_str = '''
  <!DOCTYPE html>
  <html lang="en">
  '''
  html_str = html_str + "\n<h1>Choosy Table</h1>\n"
  html_str = html_str + "\n### " + str(db) + "\n"
  html_str = html_str + "\n### " + str(star) + "\n"
  html_str = html_str + "\n<h2>Latest Info:</h2><h3>" + str(star.find_one()) + "</h3>\n</html>"
  return html_str

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('welcome'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

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