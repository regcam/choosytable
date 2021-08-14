from flask_dance.consumer.storage import BaseStorage
from flask_login import UserMixin
from app import ct, login_manager
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

e = ['Black', 'Afro-Latino', 'Bahamian', 'Jamaican', 'African']
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

@login_manager.user_loader
def load_user(email):
    u = ct.find_one({'email': email})
    if not u:
        return False
    return User(u['email'])

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