from flask import Blueprint

app = Blueprint('main', __name__)

from app.main import routes