from flask.globals import current_app
from app.main import bp
from app import ct, blueprint, client, Pagination, get_page_args, ObjectId, iel, p, igl, \
    e, request, jsonify, current_user, login_user, logout_user, login_required, login_manager
import pandas as pd
from datetime import datetime
from app.models import User, MongoStorage, MyPerson, MyCompany, MyInterview
from flask import flash, redirect, url_for, render_template
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage import BaseStorage
from flask_dance.consumer import oauth_authorized, oauth_error

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

@login_manager.user_loader
def load_user(email):
    u = ct.find_one({'email': email})
    if not u:
        return False
    return User(u['email'])

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
    oauth = find_email(info['email'])

    if oauth is None:
        oauth = info | token
        ct.insert(oauth)

    login_user(User(oauth['email']))

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False

#notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")

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

def get_css_framework():
    return current_app.config.get("CSS_FRAMEWORK", "bootstrap4")


def get_link_size():
    return current_app.config.get("LINK_SIZE", "sm")


def get_alignment():
    return current_app.config.get("LINK_ALIGNMENT", "")


def show_single_page_or_not():
    return current_app.config.get("SHOW_SINGLE_PAGE", True)

    
def get_pagination(**kwargs):
    kwargs.setdefault("record_name", "records")
    return Pagination(
        css_framework=get_css_framework(),
        link_size=get_link_size(),
        alignment=get_alignment(),
        show_single_page=show_single_page_or_not(),
        **kwargs
    )

@bp.route("/")
@bp.route("/index")
def not_logged_in():
    if google.authorized:
        google_logged_in(blueprint, google.token)
        return redirect(url_for("main.home"))
    else:
        return render_template('index.html')

@bp.route("/home")
@bp.route("/welcome")
@login_required
def home():
    #if not google.authorized:
    #    return redirect(url_for("google.login"))
    form = MyPerson()

    r_results=[]
    resp=blueprint.session.get("/oauth2/v1/userinfo").json()
    x = find_email(resp['email'])

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
            x=resp['email'],
            pagination=pagination,
            e=e, form=form)


def find_reviews():
    z="find_reviews"
    querykey=client.get(z)
    if querykey == None:
        querykey=list(ct.find({'reviews': {"$exists": True}}).sort('last_modified',-1))
        client.set(z, querykey)
    return querykey


@bp.route('/company', methods=['GET'])
@login_required
def company():
    form = MyCompany()
    page, per_page, offset = get_page_args(
        page_parameter="p", per_page_parameter="pp", pp=10)
    companies = find_reviews()
    if per_page:
        companies[offset:per_page+offset]

    pagination = get_pagination(
            p=page, 
            pp=per_page, 
            format_total=True, 
            format_number= True, 
            total=len(companies),
            page_parameter="p",
            per_page_parameter="pp",
            record_name='companies')
    return render_template('company.html', companies=companies, pagination=pagination,form=form)


@bp.route('/company', methods=['POST', 'PUT'])
@login_required
def company_post():
    form = MyCompany()
    resp = google.get("/oauth2/v1/userinfo").json()
    user = find_email(resp['email'])
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
            querykey=list(ct.find({'reviews': {"$exists": True}}).sort('last_modified',-1))
            client.replace("find_reviews",querykey)
            return redirect(request.url)
        except Exception as e:
            return render_template('error.html', error=str(e))
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


@bp.route('/company/<company_id>', methods=['GET'])
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


@bp.route('/company/<company_id>', methods=['POST', 'PUT'])
@login_required
def single_companypost(company_id):
    form = MyCompany()
    form1 = MyInterview()
    resp = google.get("/oauth2/v1/userinfo").json()
    user = find_email(resp['email'])
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
        return render_template('error.html', error="Something went wrong.  Make sure you complete your profile!")
    return redirect(request.url)


@bp.route('/person/<person_id>', methods=['GET'])
@login_required
def single_person(person_id):
    form = MyPerson()
    if request.method == 'GET':
        try:
            return redirect(url_for('main.home'))
        except:
            return render_template('error.html', error="person not found")


@bp.route('/person/<person_id>', methods=['PUT', 'POST'])
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
        return redirect(url_for('main.home'))
    else:
        return render_template('error.html', error="The form was not valid")


@bp.route('/person', methods=['GET'])
@login_required
def person():
    return redirect(url_for('main.home'))


@bp.route('/person', methods=['POST', 'PUT'])
@login_required
def person_post():
    form = MyPerson()
    resp = google.get("/oauth2/v1/userinfo").json()
    if form.validate_on_submit():
        x=ct.insert_one(
            {'created': datetime.now(),
            '_id': ObjectId(), 
            'name': request.form.get('name'), 
            'email': resp['email'],
            'ethnicity': request.form.get('ethnicity'),
            'gender': request.form.get('gender'),
            'location': request.form.get('location'),
            'age': request.form.get('age')})
        return redirect(url_for('main.home'))
    else:
        return render_template('error.html', error="Form wasn't valid")


@bp.route('/forgetme/<user>')
@login_required
def forgetme(user):
    resp = google.get("/oauth2/v1/userinfo").json()
    if find_email(resp['email']):
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
        client.delete_multi([str(user)+"_reviews"],resp['email'])
    return redirect(url_for('main.home'))


@bp.route('/deletereview/<id>')
@login_required
def deletereview(id):
    resp = google.get("/oauth2/v1/userinfo").json()
    user = find_email(resp['email'])
    if user and ct.find_one({'reviews.user': str(user['_id'])}):
        ct.update(
            {'reviews._id': id}, 
            {'$pull': {'reviews': {'_id': id}}}
        )
        client.delete_multi([str(user['_id'])+"_reviews", resp['email']])
    return redirect(url_for('main.home'))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return render_template('bye.html')