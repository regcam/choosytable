from flask_dance.consumer.storage import BaseStorage
from flask_login import UserMixin
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from .constants import (
    ETHNICITY_OPTIONS,
    GENDER_OPTIONS,
    POSITION_OPTIONS,
    AGE_OPTIONS,
    LOCATION_OPTIONS,
    RATING_OPTIONS,
    INTERVIEW_OUTCOMES,
    EMPLOYEE_STATUS
)

class MongoStorage(BaseStorage):
    def __init__(self, email):
        super(MongoStorage, self).__init__()
        self.email = email

    def get(self, blueprint):
        # Import here to avoid circular imports
        from app import ct
        u = ct.find_one({'email': self.email})
        if u is None:
            return None
        else:
            return u

    def set(self, blueprint, token):
        from app import ct
        ct.update_one({'email': self.email},{'$set': {'token': token}})

    def delete(self, blueprint):
        from app import ct
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
    gender = RadioField('Your Gender:', choices=[(x, x) for x in GENDER_OPTIONS])
    age = SelectField('Your Age:', choices=[(x, x) for x in AGE_OPTIONS])
    ethnicity = SelectField('Your Ethnicity:', choices=[(x, x) for x in ETHNICITY_OPTIONS])
    location = SelectField('Your Location:', choices=[(x, x) for x in LOCATION_OPTIONS])
    submit = SubmitField("Submit")

class MyCompany(FlaskForm):
    company = StringField('Name of Company', validators=[DataRequired()])
    reviews = TextAreaField('Your Review', validators=[DataRequired()])
    rating = RadioField('Your Rating', choices=[(str(x), str(x)) for x in RATING_OPTIONS])
    submit = SubmitField("Submit")

class MyInterview(FlaskForm):
    ie = SelectField('Interviewer\'s Ethnicity:', choices=[(x, x) for x in ETHNICITY_OPTIONS])
    position = SelectField('Position Title:', choices=POSITION_OPTIONS)
    employee = RadioField('Are you an employee here?', choices=EMPLOYEE_STATUS)
    win = RadioField('Were you offered the position?', choices=INTERVIEW_OUTCOMES)  
    submit = SubmitField("Submit")
