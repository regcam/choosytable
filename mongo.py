from flask import Flask, redirect, url_for, session, render_template, request, jsonify, flash
from flask_pymongo import PyMongo, ObjectId
from bson import json_util, objectid
from datetime import datetime
import os
from flask_dance.contrib.google import make_google_blueprint, google
from flask_paginate import Pagination, get_page_args
from flask_navigation import Navigation
from functools import lru_cache
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, RadioField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'choosytable'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/choosytable'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.urandom(24).hex()
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID")
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get(
    "GOOGLE_CLIENT_SECRET")
blueprint = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(blueprint, url_prefix="/login")

mongo = PyMongo(app)
ct = mongo.db.choosytable
db = mongo.db
nav = Navigation(app)

nav.Bar('top', [
    nav.Item('Home', 'person'),
    nav.Item('Companies', 'company'),
    nav.Item('People', 'person'),
    nav.Item('Logout', 'logout')
])

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

labels = ['1 Star','2 Stars','3 Stars','4 Stars','5 Stars']
labels1 = ['Offered the Job %','No Offer %']
labels2 = ['# of Interviews']

iel = ['White','Asian','Latino','Black','Afro-Latino',
'African','Indigenous People','Pacific Islander', 'Unspecified']
igl = ['Female','Male','Transgender','Agender','Unspecified']
p = ['Software Engineer','Staff Engineer','Lead Engineer',
'Architect','Software Engineer Manager','Technical Manager','Technical Director',
'VP','CTO','Network Engineer','Principal Architect','QA Engineer','SRE','SDET',
'Project Manager','Program Manager','DevOps Engineer','Systems Admin',
'DBA','Operations Engineer']
age = ['18-24','25-34','35-44','45-54','55-64','65-74','75+']

class MyPerson(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    email = EmailField('Your Email', validators=[DataRequired()])
    gender = RadioField('Your Gender:', choices=[(x) for x in igl])
    age = SelectField('Your Age:', choices=[(x) for x in age])
    ethnicity = SelectField('Your Ethnicity:', choices=[(x) for x in iel])
    submit = SubmitField("Submit")

class MyCompany(FlaskForm):
    company = StringField('Name of Company', validators=[DataRequired()])
    reviews = TextAreaField('Your Review', validators=[DataRequired()])
    rating = RadioField('Your Rating', choices=[x for x in range(1,6)])
    submit = SubmitField("Submit")

class MyInterview(FlaskForm):
    ie = SelectField('Interviewer\'s Ethnicity:', choices=[(x) for x in iel])
    position = SelectField('Position Title:', choices=[(x) for x in p])
    employee = RadioField('Are you an employee here?', choices=[('n','Yes'),('n','No')])
    win = RadioField('Were you offered the position?', choices=[('y','Yes'),('n','No'),('o','Offered a Different Position')])  
    submit = SubmitField("Submit")


#@lru_cache
@app.before_request
def before_request():
    if not google.authorized and "google" not in request.path:
        return render_template("index.html")
    else:
        session['resp'] = google.get("/oauth2/v1/userinfo").json()


def find_creatorreviews(y):
    return ct.find({'reviews.user': str(y['_id'])},{'reviews':1,'_id':1,'company':1}).sort('last_modified',-1)


def find_email(z):
    return ct.find_one({'email': z})


def get_pagination(**kwargs):
    kwargs.setdefault("record_name", "records")
    return Pagination(
        css_framework=get_css_framework(),
        link_size=get_link_size(),
        alignment=get_alignment(),
        show_single_page=show_single_page_or_not(),
        **kwargs
    )


def get_css_framework():
    return app.config.get("CSS_FRAMEWORK", "bootstrap4")


def get_link_size():
    return app.config.get("LINK_SIZE", "sm")


def get_alignment():
    return app.config.get("LINK_ALIGNMENT", "")


def show_single_page_or_not():
    return app.config.get("SHOW_SINGLE_PAGE", True)


@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route("/welcome")
def home():
    form = MyPerson()
    e = ['Black', 'Afro-Latino', 'Bahamian', 'Jamaican', 'African']
    r_results=[]
    x = find_email(session['resp']['email'])
    reviewcount=0
    if x is not None:
        page, per_page, offset = get_page_args(
        page_parameter="p", per_page_parameter="pp", pp=10)

        r = list(find_creatorreviews(x))
            
        for indx,key in enumerate(r):
            r_results.append((key['reviews'],key['company']))
            reviewcount+=1

        if per_page:
            r_results= r_results[offset:(per_page + offset if per_page is not None else None)]

        form.gender.default = x['gender']
        form.age.default = x['age']
        form.ethnicity.default = x['ethnicity']
        form.process()
        
        pagination = get_pagination(
            p=page, 
            pp=per_page, 
            format_total=True, 
            format_number= True, 
            total=reviewcount,
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
            x=session['resp']['email'],
            pagination=pagination,
            e=e, form=form)


#@lru_cache
def find_reviews():
    return ct.find({'reviews': {"$exists": True}}).sort('last_modified',-1)


#@lru_cache
@app.route('/company', methods=['GET'])
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
def company_post():
    form = MyCompany()
    user = find_email(session['resp']['email'])
    if form.validate_on_submit():
        try:
            ct.insert(
                {
                    'created': datetime.now(),
                    'company': request.form.get('company'),
                    'reviews': [
                        {
                            'review':request.form.get('reviews'),
                            'rating':int(request.form.get('rating')),
                            'user': str(user['_id'])
                        }
                    ],
                    'reviews_avg': 0
                }
            )
            return redirect(request.url)
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        flash('All fields are required.')
        return redirect(request.url)


#@lru_cache
def findone_company(c):
    return ct.find_one({'_id': ObjectId(c)})


def your_chances(success):
    return (success['my_y']/(success['y']+success['n']+success['o']))*100


#@lru_cache
@app.route('/company/<company_id>', methods=['GET'])
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
    l={'one':0,'two':0,'three':0,'four':0,'five':0}
    values=[]
    success={'y':0,'n':0,'o':0,'my_y':0,'my_o':0,'my_n':0}
    for i in range(len(singlecompany['reviews'])):
        if singlecompany['reviews'][i]['rating']==1:
            l['one']+=1
        elif singlecompany['reviews'][i]['rating']==2:
            l['two']+=1
        elif singlecompany['reviews'][i]['rating']==3:
            l['three']+=1
        elif singlecompany['reviews'][i]['rating']==4:
            l['four']+=1
        elif singlecompany['reviews'][i]['rating']==5:
            l['five']+=1

    for k in l.values():
        values.append(format(k/len(singlecompany['reviews']), '.3f')) if len(singlecompany['reviews'])>0 else values.append(0)

    positionDict={}
    x=find_email(session['resp']['email'])
    values1=[0,0]
    if 'interviews' in singlecompany and len(singlecompany['interviews'])>0:
        for a in range(len(singlecompany['interviews'])):
            if singlecompany['interviews'][a]['win'] == "y":
                if singlecompany['interviews'][a]['user_gender']==x['gender'] and singlecompany['interviews'][a]['user_ethnicity']==x['ethnicity']:
                    success['my_y']+=1
                    success['y']+=1
                else:
                     success['y']+=1
            elif singlecompany['interviews'][a]['win'] == "o":
                if singlecompany['interviews'][a]['user_gender']==x['gender'] and singlecompany['interviews'][a]['user_ethnicity']==x['ethnicity']:
                    success['my_o']+=1
                    success['o']+=1
                else:
                     success['o']+=1
            else:
                if singlecompany['interviews'][a]['user_gender']==x['gender'] and singlecompany['interviews'][a]['user_ethnicity']==x['ethnicity']:
                    success['my_n']+=1
                    success['n']+=1
                else:
                     success['n']+=1
            if positionDict.get(singlecompany['interviews'][a]['position']) is None:
                positionDict[singlecompany['interviews'][a]['position']]=1
            else:
                positionDict[singlecompany['interviews'][a]['position']]=\
                    positionDict.get(singlecompany['interviews'][a]['position'])+1

        values1=[format(success['y']/len(singlecompany['interviews']), '.3f'),
        format(success['n']/len(singlecompany['interviews']), '.3f')]
        ychance=your_chances(success)
        
        pagination = get_pagination(
            p=page, 
            pp=per_page, 
            format_total=True, 
            format_number= True, 
            total=len(sc_results),
            page_parameter="p",
            per_page_parameter="pp",
            record_name=singlecompany['company'])

        return render_template('singlecompany.html', singlecompany=singlecompany, pagination=pagination, 
    set=zip(values,labels,colors),iel=iel,igl=igl,p=p,set1=zip(values1,labels1,colors),
    set2=zip(positionDict.items(),colors),form=form,form1=form1,ychance=ychance,sc_results=sc_results)
    else:
        pagination = Pagination(page=page, total=len(
            sc_results), record_name=singlecompany['company'])
        return render_template('singlecompany.html', singlecompany=singlecompany, pagination=pagination, 
        set=zip(values,labels,colors),iel=iel,igl=igl,p=p,
        set2=zip(positionDict.items(),colors),form=form,form1=form1,sc_results=sc_results)


@app.route('/company/<company_id>', methods=['POST', 'PUT'])
def single_companypost(company_id):
    form = MyCompany()
    form1 = MyInterview()
    user = find_email(session['resp']['email'])
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
                        'ethnicity':user['ethnicity']
                    },

                },
            },
            upsert=True
        )
        reviews_avg=list(ct.aggregate(
                [
                    { '$match': { '_id': ObjectId(company_id) } },
                    { '$unwind': "$reviews" },
                    { '$group': { '_id': None, 'reviews_avg':{'$avg': '$reviews.rating'} } }  
                ]
            ))
        ct.update_one({'_id': ObjectId(company_id)},{'$set': 
        {'reviews_avg': reviews_avg[0]['reviews_avg'],'last_modified': datetime.now()}})
    elif form1.validate_on_submit() and user:
        ct.update_one(
            {'_id': ObjectId(company_id)},
            {
                '$push':
                {
                    'interviews':
                    {
                        '_id': str(ObjectId()),
                        'ie':request.form.get('ie'),
                        'position': request.form.get('position'),
                        'employee': request.form.get('employee'),
                        'gender': user['gender'],
                        'user': str(user['_id']),
                        'user_gender':user['gender'],
                        'user_ethnicity':user['ethnicity'],
                        'win': request.form.get('win')
                    }
                },
                '$set': {'last_modified': datetime.now()}
            },
            upsert=True
        )
    else:
        return jsonify({'error': "Something went wrong.  Make sure you complete your profile!"})
    return redirect(request.url)


#@lru_cache
@app.route('/person/<person_id>', methods=['GET'])
def single_person(person_id):
    form = MyPerson()
    if request.method == 'GET':
        try:
            return json_util.dumps(ct.find_one({'_id': ObjectId(person_id)}))
        except:
            return jsonify({'error': 'person not found'})


@app.route('/person/<person_id>', methods=['PUT', 'POST'])
def singleupdate_person(person_id):
    form = MyPerson()
    if form.validate_on_submit():
        ct.update(
            {'_id': ObjectId(person_id)},
            {
                '$set': {
                    'name': request.form.get('name'),
                    'gender': request.form.get('gender'),
                    'age': request.form.get('age'),
                    'ethnicity': request.form.get('ethnicity'),
                    "last_modified": datetime.now()}
            }
        )
        ct.update(
            {'interviews.user': person_id},
            {
                '$set': {
                    'user_gender': request.form.get('gender'),
                    'user_ethnicity': request.form.get('ethnicity')
                }
            }
        )
        ct.update(
            {'reviews.user': person_id},
            {
                '$set': {
                    'gender': request.form.get('gender'),
                    'ethnicity': request.form.get('ethnicity')
                }
            }
        )
        return redirect(request.url)
    else:
        return jsonify({'error': "The form was not valid"})


#@lru_cache
@app.route('/person', methods=['GET'])
def person():
    return redirect(url_for('home'))


@app.route('/person', methods=['POST', 'PUT'])
def person_post():
    form = MyPerson()
    if form.validate_on_submit():
        x=ct.insert_one(
            {'created': datetime.now(),
            '_id': ObjectId(), 
            'name': request.form.get('name'), 
            'email': request.form.get('email'), 
            'ethnicity': request.form.get('ethnicity'),
            'gender': request.form.get('gender'),
            'age': request.form.get('age')})
        find_email.cache_clear()
        return redirect(url_for('home'))
    else:
        return jsonify({'error': "Form wasn't valid"})


@app.route('/forgetme/<user>')
def forgetme(user):
    ct.update(
        {'reviews.user': user}, 
        {'$pull': {'reviews': {'user': user}}}
    )
    ct.update(
        {'interviews.user': user}, 
        {'$pull': {'interviews': {'user': user}}}
    )
    ct.remove(
        {'_id': ObjectId(user)}, 
    )
    find_email.cache_clear()
    return redirect(url_for('home'))


@app.route('/deletereview/<id>')
def deletereview(id):
    ct.update(
        {'reviews._id': id}, 
        {'$pull': {'reviews': {'_id': id}}}
    )
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('session', None)
    return render_template('bye.html')


if __name__ == '__main__':
    app.run(debug=True)