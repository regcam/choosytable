from flask import Flask, redirect, url_for, session, render_template, request, jsonify, flash
from flask_pymongo import PyMongo, ObjectId
from bson import json_util, objectid
from datetime import datetime
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage import BaseStorage
from flask_paginate import Pagination, get_page_args
from flask_navigation import Navigation
from flask_wtf import FlaskForm
from pandas.core.frame import DataFrame
from pandas.core.groupby.generic import DataFrameGroupBy
from wtforms import StringField, IntegerField, TextAreaField, RadioField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import pandas as pd
from pymemcache.client.base import Client
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin

class MongoStorage(BaseStorage):
    def __init__(self, email):
        super(MongoStorage, self).__init__()
        self.email = email

    def get(self, blueprint):
        u = ct.find_one({'email': self.email})
        if u is None:
            return None
        else:
            return u

    def set(self, blueprint, token):
        ct.update_one({'email': self.email},{'$set': {'token': token}})

    def delete(self, blueprint):
        ct.update(
            {'email': self.email}, 
            {'$pull': {'email': self.email}}
        )

class JsonSerde(object):
    def serialize(self, key, value):
        if isinstance(value, str):
            return value.encode('utf-8'), 1
        return json_util.dumps(value).encode('utf-8'), 2

    def deserialize(self, key, value, flags):
       if flags == 1:
           return value.decode('utf-8')
       if flags == 2:
           return json_util.loads(value.decode('utf-8'))
       raise Exception("Unknown serialization format")

client = Client('localhost', serde=JsonSerde())

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'choosytable'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/choosytable'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.urandom(24).hex()
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID")
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get(
    "GOOGLE_CLIENT_SECRET")
blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    offline=True,
    reprompt_consent=True
    )
app.register_blueprint(blueprint, url_prefix="/login")

# setup login manager
login_manager = LoginManager()
login_manager.login_view = "google.login"
login_manager.init_app(app)

mongo = PyMongo(app)
ct = mongo.db.choosytable
nav = Navigation(app)


class User(UserMixin):
    def __init__(self, email):
        self.email = email

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return str(self.email)

    @login_manager.user_loader
    def load_user(email):
        u = ct.find_one({'email': email})
        if not u:
            return False
        return User(u['email'])


nav.Bar('top', [
    nav.Item('Home', 'person'),
    nav.Item('Companies', 'company'),
    nav.Item('People', 'person'),
    nav.Item('Logout', 'logout')
])

def get_css_framework():
    return app.config.get("CSS_FRAMEWORK", "bootstrap4")


def get_link_size():
    return app.config.get("LINK_SIZE", "sm")


def get_alignment():
    return app.config.get("LINK_ALIGNMENT", "")


def show_single_page_or_not():
    return app.config.get("SHOW_SINGLE_PAGE", True)


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

class MyPerson(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    email = EmailField('Your Email', validators=[DataRequired()])
    gender = RadioField('Your Gender:', choices=[(x) for x in igl])
    age = SelectField('Your Age:', choices=[(x) for x in age])
    ethnicity = SelectField('Your Ethnicity:', choices=[(x) for x in iel])
    location = SelectField('Your Location:', choices=[(x) for x in location])
    submit = SubmitField("Submit")

class MyCompany(FlaskForm):
    company = StringField('Name of Company', validators=[DataRequired()])
    reviews = TextAreaField('Your Review', validators=[DataRequired()])
    rating = RadioField('Your Rating', choices=[x for x in range(1,6)])
    submit = SubmitField("Submit")

class MyInterview(FlaskForm):
    ie = SelectField('Interviewer\'s Ethnicity:', choices=[(x) for x in iel])
    position = SelectField('Position Title:', choices=[x for x in p])
    employee = RadioField('Are you an employee here?', choices=[('y','Yes'),('n','No')])
    win = RadioField('Were you offered the position?', choices=[('y','Yes'),('n','No'),('o','Offered a Different Position')])  
    submit = SubmitField("Submit")


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


@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/welcome")
def home():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.txt
    email=resp.json()['email']
    blueprint.storage = MongoStorage(email)
    token=google.token
    all=resp.json()   
    try:
        user=find_email(email)
        if user is None:
            raise ValueError("User not found")
    except:
        user=ct.insert(resp.json())
        MongoStorage.set(MongoStorage(email),blueprint,token)
        user=find_email(email)

    login_user(User(email))
    form = MyPerson()
    e = ['Black', 'Afro-Latino', 'Bahamian', 'Jamaican', 'African']
    r_results=[]
    x = user

    if x is not None:
        page, per_page, offset = get_page_args(
        page_parameter="p", per_page_parameter="pp", pp=10)

        r = find_creatorreviews(x)
        for key in r:
            r_results.append((key['reviews'],key['_id'],key['company']))

        if per_page:
            r_results= r_results[offset:(per_page + offset if per_page is not None else None)]

        form.gender.default = x.get('gender') or 'Unspecified'
        form.age.default = x.get('age') or '18-24'
        form.ethnicity.default = x.get('ethnicity') or 'Unspecified'
        form.location.default = x.get('location') or 'GA'
        form.process()
        
        pagination = get_pagination(
            p=page, 
            pp=per_page, 
            format_total=True, 
            format_number= True, 
            total=len(r_results),
            page_parameter="p",
            per_page_parameter="pp",
            record_name='Your latest reviews')
        return render_template(
            'person.html',
            x=x,
            r_results=r_results,
            e=e,
            pagination=pagination, 
            form=form)
    else:
        page, per_page, offset = get_page_args(
        page_parameter="p", per_page_parameter="pp", pp=10)
        pagination = get_pagination(
            p=page, 
            pp=per_page, 
            format_total=True, 
            format_number= True, 
            total=0,
            page_parameter="p",
            per_page_parameter="pp",
            record_name='Your latest reviews')
        return render_template(
            'person.html',
            x=resp.json()['email'],
            pagination=pagination,
            e=e, form=form)


def find_reviews():
    z="find_reviews"
    querykey=client.get(z)
    if querykey == None:
        querykey=ct.find({'reviews': {"$exists": True}}).sort('last_modified',-1)
        client.set(z,querykey)
    return querykey


@app.route('/company', methods=['GET'])
@login_required
def company():
    form = MyCompany()
    page, per_page, offset = get_page_args(
        page_parameter="p", per_page_parameter="pp", pp=10)
    companies = find_reviews()
    if per_page:
        companies.limit(per_page).skip(offset)
    pagination = get_pagination(
            p=page, 
            pp=per_page, 
            format_total=True, 
            format_number= True, 
            total=companies.count(),
            page_parameter="p",
            per_page_parameter="pp",
            record_name='companies')
    return render_template('company.html', companies=companies, pagination=pagination,form=form)


@app.route('/company', methods=['POST', 'PUT'])
@login_required
def company_post():
    form = MyCompany()
    resp = google.get("/oauth2/v1/userinfo")
    user = find_email(resp.json()['email'])
    if form.validate_on_submit():
        try:
            ct.insert(
                {
                    'created': datetime.now(),
                    'company': request.form.get('company'),
                    'reviews': [
                        {
                            '_id': str(ObjectId()),
                            'review':request.form.get('reviews'),
                            'rating':int(request.form.get('rating')),
                            'user': str(user['_id'])
                        }
                    ]
                }
            )
            client.delete("find_reviews")
            return redirect(request.url)
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        flash('All fields are required.')
        return redirect(request.url)


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


@app.route('/company/<company_id>', methods=['GET'])
@login_required
def single_company(company_id):
    form = MyCompany()
    form1 = MyInterview()
    page, per_page, offset = get_page_args(
        page_parameter="p", per_page_parameter="pp", pp=10)

    singlecompany = findone_company(company_id)
    sc_results=[]
    if per_page:
        sc_results.append(singlecompany['reviews'])
        sc_results=sc_results[0][offset:(per_page + offset if per_page is not None else None)]

    reviews=pd.DataFrame(singlecompany['reviews'])
    rating_avg=reviews['rating'].mean()
    winDict=pd_interviews(p,singlecompany)
        
    pagination = get_pagination(
        p=page, 
        pp=per_page, 
        format_total=True, 
        format_number= True, 
        total=len(sc_results),
        page_parameter="p",
        per_page_parameter="pp",
        record_name=singlecompany['company'])
        
    return render_template('singlecompany.html', singlecompany=singlecompany, 
    pagination=pagination, iel=iel,igl=igl,p=p,form=form,form1=form1,
    winDict=winDict,sc_results=sc_results,rating_avg=rating_avg)


@app.route('/company/<company_id>', methods=['POST', 'PUT'])
@login_required
def single_companypost(company_id):
    form = MyCompany()
    form1 = MyInterview()
    resp = google.get("/oauth2/v1/userinfo")
    user = find_email(resp.json()['email'])
    if form.validate_on_submit() and user:
        ct.update_one(
            {'_id': ObjectId(company_id)},
            {
                '$push':
                {
                    'reviews':
                    {
                        '_id': str(ObjectId()),
                        'review': request.form.get('reviews'),
                        'rating': int(request.form.get('rating')),
                        'user': str(user['_id']),
                        'gender':user['gender'],
                        'location':user['location'],
                        'ethnicity':user['ethnicity']
                    },

                },
            },
            upsert=True
        )

        ct.update_one({'_id': ObjectId(company_id)},{'$set': 
        {'last_modified': datetime.now()}})

        client.delete_multi([str(user['_id'])+"_reviews",company_id])
    elif form1.validate_on_submit() and user:
        ct.update_one(
            {'_id': ObjectId(company_id)},
            {
                '$push':
                {
                    request.form.get('position'):
                    {
                        '_id': str(ObjectId()),
                        'employee': request.form.get('employee'),
                        'user': str(user['_id']),
                        'user_gender':user['gender'],
                        'user_ethnicity':user['ethnicity'],
                        'user_location':user['location'],
                        'win': request.form.get('win')
                    }
                },
                '$set': {'last_modified': datetime.now()}
            },
            upsert=True
        )
        client.delete_multi([company_id, company_id+"_pd_interviews"])
    else:
        return jsonify({'error': "Something went wrong.  Make sure you complete your profile!"})
    return redirect(request.url)


@app.route('/person/<person_id>', methods=['GET'])
@login_required
def single_person(person_id):
    form = MyPerson()
    if request.method == 'GET':
        try:
            return redirect(url_for('home'))
        except:
            return jsonify({'error': 'person not found'})


@app.route('/person/<person_id>', methods=['PUT', 'POST'])
@login_required
def singleupdate_person(person_id):
    form = MyPerson()
    if form.validate_on_submit():
        ct.update_one(
            {'_id': ObjectId(person_id)},
            {
                '$set': {
                    'name': request.form.get('name'),
                    'gender': request.form.get('gender'),
                    'age': request.form.get('age') or '18-24',
                    'ethnicity': request.form.get('ethnicity') or 'Unknown',
                    'location': request.form.get('location') or 'GA',
                    "last_modified": datetime.now()}
            }
        )
        ct.update_one(
            {'interviews.user': person_id},
            {
                '$set': {
                    'user_gender': request.form.get('gender'),
                    'user_location': request.form.get('location'),
                    'user_ethnicity': request.form.get('ethnicity')
                }
            }
        )
        ct.update_one(
            {'reviews.user': person_id},
            {
                '$set': {
                    'gender': request.form.get('gender'),
                    'location': request.form.get('location'),
                    'ethnicity': request.form.get('ethnicity')
                }
            }
        )
        x=ct.find_one({'_id': ObjectId(person_id)})
        client.delete(x['email'])
        return redirect(url_for('home'))
    else:
        return jsonify({'error': "The form was not valid"})


@app.route('/person', methods=['GET'])
@login_required
def person():
    return redirect(url_for('home'))


@app.route('/person', methods=['POST', 'PUT'])
@login_required
def person_post():
    form = MyPerson()
    resp = google.get("/oauth2/v1/userinfo")
    if form.validate_on_submit():
        x=ct.insert_one(
            {'created': datetime.now(),
            '_id': ObjectId(), 
            'name': request.form.get('name'), 
            'email': resp.json()['email'],
            'ethnicity': request.form.get('ethnicity'),
            'gender': request.form.get('gender'),
            'location': request.form.get('location'),
            'age': request.form.get('age')})
        return redirect(url_for('home'))
    else:
        return jsonify({'error': "Form wasn't valid"})


@app.route('/forgetme/<user>')
@login_required
def forgetme(user):
    resp = google.get("/oauth2/v1/userinfo")
    if find_email(resp.json()['email'],):
        ct.update(
            {'reviews.user': user}, 
            {'$pull': {'reviews': {'user': user}}}
        )
        ct.update(
            {'interviews.user': user}, 
            {'$pull': {'interviews': {'user': user}}}
        )
        ct.remove(
            {'_id': ObjectId(user)} 
        )
        resp = google.get("/oauth2/v1/userinfo")
        client.delete_multi([str(user['_id'])+"_reviews"],resp.json()['email'],)
    return redirect(url_for('home'))


@app.route('/deletereview/<id>')
@login_required
def deletereview(id):
    resp = google.get("/oauth2/v1/userinfo")
    user = find_email(resp.json()['email'])
    if user and ct.find_one({'reviews.user': str(user['_id'])}):
        ct.update(
            {'reviews._id': id}, 
            {'$pull': {'reviews': {'_id': id}}}
        )
        client.delete_multi([str(user['_id'])+"_reviews", resp.json()['email']])
    return redirect(url_for('home'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return render_template('bye.html')


if __name__ == '__main__':
    app.run(threaded=True)