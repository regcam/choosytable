from flask import Flask, redirect, url_for, session, render_template, request, jsonify, g
from waitress import serve
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_paginate import Pagination, get_page_parameter
from flask_navigation import Navigation
from functools import lru_cache


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.urandom(24).hex()
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID")
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get(
    "GOOGLE_CLIENT_SECRET")
blueprint = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(blueprint, url_prefix="/login")

mongo = PyMongo(app)
star = mongo.db.stars
db = mongo.db
nav = Navigation(app)

nav.Bar('top', [
    nav.Item('Home', 'person'),
    nav.Item('Companies', 'company'),
    nav.Item('People', 'person'),
    nav.Item('Logout', 'logout'),
])

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

labels = ['1 Star','2 Stars','3 Stars','4 Stars','5 Stars']
labels1 = ['Offered the Job %','No Offer %']
labels2 = ['# of Interviews']

iel = ['White','Asian','Latino','Black','Afro-Latino','African','Indigenous People','Pacific Islander']
igl = ['Female','Male','Transgender','Agender']
p = ['Software Engineer','Staff Engineer','Lead Engineer',
'Architect','Software Engineer Manager','Technical Manager','Technical Director',
'VP','CTO','Network Engineer','Principal Architect','QA Engineer','SRE','SDET',
'Project Manager','Program Manager','DevOps Engineer','Systems Admin',
'DBA','Operations Engineer']

@lru_cache
@app.before_request
def before_request():
    if not google.authorized and "google" not in request.path:
        return render_template("index.html")
    else:
        session['resp'] = google.get("/oauth2/v1/userinfo").json()


#@lru_cache
def find_creatorreviews(y):
    return star.find(
      {
        "$and": [
          {'creator': y}, 
          {'reviews': {"$exists": True}}
        ]
      })


#@lru_cache
def find_email(z):
    return star.find_one({'email': z})


def invalidate_cache():
    find_creatorreviews.cache_clear()
    find_reviews.cache_clear()
    findone_company.cache_clear()

@lru_cache
@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/welcome")
def home():
    e = ['Black', 'Afro-Latino', 'Bahamian', 'Jamaican', 'African']
    x = find_email(session['resp']['email'])
    r = find_creatorreviews(x['name'])
    if r is not None:
        search = False
        q = request.args.get('q')
        if q:
            search = True
        page = request.args.get(get_page_parameter(), type=int, default=1)
        pagination = Pagination(
            page=page, total=r.count(), search=search, record_name='Your latest reviews')
        return render_template(
            'person.html',
            x=x,
            r=r,
            e=e,
            pagination=pagination)
    else:
        return render_template(
            'person.html',
            email=session['resp']['email'],
            name=session['resp']['name'],
            e=e)


#@lru_cache
def find_reviews():
    return star.find({'reviews': {"$exists": True}})


@lru_cache
@app.route('/company', methods=['GET'])
def company():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    companies = find_reviews()
    pagination = Pagination(
        page=page, total=companies.count(), search=search, record_name='companies')
    return render_template('company.html', companies=companies, pagination=pagination)


@app.route('/company', methods=['POST', 'PUT'])
def company_post():
    try:
        star.insert(
            {
                'created': datetime.now(),
                'company': request.form['company'],
                'creator': session['resp']['name'],
                'reviews': [
                    {
                        'review': request.form['reviews'],
                        'rating':request.form['rating']
                    }
                ]
            }
        )
        #find_reviews.cache_clear()
        #find_reviews()
        return redirect(request.url)
    except Exception as e:
        return jsonify({'error': str(e)})


@lru_cache
def findone_company(c):
    return star.find_one({'_id': ObjectId(c)})


@lru_cache
@app.route('/company/<company_id>', methods=['GET'])
def single_company(company_id):
    if request.method == 'GET':
        search = False
        q = request.args.get('q')
        if q:
            search = True
        page = request.args.get(get_page_parameter(), type=int, default=1)
        singlecompany = findone_company(company_id)
        l={'one':0,'two':0,'three':0,'four':0,'five':0}
        values=[]
        success={'y':0,'n':0}
        for i in range(len(singlecompany['reviews'])):
            if singlecompany['reviews'][i]['rating']=="1":
                l['one']+=1
            elif singlecompany['reviews'][i]['rating']=="2":
                l['two']+=1
            elif singlecompany['reviews'][i]['rating']=="3":
                l['three']+=1
            elif singlecompany['reviews'][i]['rating']=="4":
                l['four']+=1
            elif singlecompany['reviews'][i]['rating']=="5":
                l['five']+=1

        for k in l.values():
            values.append(format(k/len(singlecompany['reviews']), '.3f'))
        
        positionDict={}

        for a in range(len(singlecompany['interviews'])):
            if singlecompany['interviews'][a]['win'] == "y":
                success['y']+=1
            else:
                success['n']+=1
            if positionDict.get(singlecompany['interviews'][a]['position']) is None:
                positionDict[singlecompany['interviews'][a]['position']]=1
            else:
                positionDict[singlecompany['interviews'][a]['position']]=\
                    positionDict.get(singlecompany['interviews'][a]['position'])+1

        values1=[format(success['y']/len(singlecompany['interviews']), '.3f'),
        format(success['n']/len(singlecompany['interviews']), '.3f')] 
        
        pagination = Pagination(page=page, total=len(
            singlecompany['reviews']), search=search, record_name=singlecompany['company'])
        return render_template('singlecompany.html', singlecompany=singlecompany, pagination=pagination, 
        set=zip(values,labels,colors),iel=iel,igl=igl,p=p,set1=zip(values1,labels1,colors),
        set2=zip(positionDict.items(),colors))


@app.route('/company/<company_id>', methods=['POST', 'PUT'])
def single_companypost(company_id):
    try:
        if None not in [request.form.get('reviews'),request.form.get('rating')]:
            star.update_one(
                {'_id': ObjectId(company_id)},
                {
                    '$push':
                    {
                        'reviews':
                        {
                            'review': request.form.get('reviews'),
                            'rating': request.form.get('rating')
                        }
                    },
                    '$set': {'last_modified': datetime.now()}
                },
                upsert=True
            )
        elif None not in [request.form.get('ie'),request.form.get('ig'),
        request.form.get('position'),request.form.get('win')]:
            star.update_one(
                {'_id': ObjectId(company_id)},
                {
                    '$push':
                    {
                        'interviews':
                        {
                            'ie':request.form.get('ie'),
                            'gender': request.form.get('ig'),
                            'position': request.form.get('position'),
                            'win': request.form.get('win')
                        }
                    },
                    '$set': {'last_modified': datetime.now()}
                },
                upsert=True
            )
        findone_company.cache_clear()
        findone_company(company_id)
        return redirect(request.url)
    except Exception as e:
        return jsonify({'error': str(e)})


@lru_cache
@app.route('/person/<person_id>', methods=['GET'])
def single_person(person_id):
    if request.method == 'GET':
        try:
            return json_util.dumps(star.find_one({'_id': ObjectId(person_id)}))
        except:
            return jsonify({'error': 'person not found'})


@app.route('/person/<person_id>', methods=['PUT', 'POST'])
def singleupdate_person(person_id):
    try:
        star.update(
            {'_id': ObjectId(person_id)},
            {
                '$set': {
                    'name': request.form['name'],
                    'ethnicity': request.form['ethnicity'],
                    "last_modified": datetime.now()}
            }
        )
        #invalidate_cache()
        return redirect(request.url)
    except Exception as e:
        return jsonify({'error': str(e)})


@lru_cache
@app.route('/person', methods=['GET'])
def person():
    return redirect("/home")


@app.route('/person', methods=['POST', 'PUT'])
def person_post():
    try:
        x=star.insert_one(
            {'created': datetime.now(), 
            'name': session['resp']['name'], 
            'email': session['resp']['email'], 
            'ethnicity': request.form['ethnicity']})
        find_creatorreviews.cache_clear()
        find_creatorreviews(x.name)
        return redirect(request.url)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route("/logout")
def logout():
    session.clear()
    return render_template('bye.html')


if __name__ == '__main__':
    #app.run(debug=True)
    serve(app, host='0.0.0.0', port=5000, url_scheme='http')
