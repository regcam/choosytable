from flask import Blueprint
from app import app

bp = Blueprint('main', __name__, template_folder='../templates')

from . import routes