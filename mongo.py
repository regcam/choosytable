from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

mongo = PyMongo(app)
star = mongo.db.stars

db = mongo.db
print ("MongoDB Database:", mongo.db)

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

@app.route("/")
def connect_mongo():
  html_str = '''
  <!DOCTYPE html>
  <html lang="en">
  '''
  # Have Flask return some MongoDB information
  html_str = html_str + "\n<h1>Choosy Table</h1>\n"
  #html_str = html_str + "\n## mongo.cx client instance:" + str(mongo.cx) + "\n"
  html_str = html_str + "\n### " + str(db) + "\n"
  html_str = html_str + "\n### " + str(star) + "\n"

  # Get a MongoDB document using PyMongo's find_one() method
  html_str = html_str + "\n<h2>Latest Info:</h2><h3>" + str(star.find_one()) + "</h3>\n</html>"

  return html_str

if __name__ == '__main__':
    app.run(debug=True)