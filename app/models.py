from flask_dance.consumer.storage import BaseStorage
from flask_login import UserMixin
from app.__init__ import ct, nav, login_manager, e, iel, igl, p, age, location
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

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