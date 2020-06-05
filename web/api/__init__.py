from flask import Blueprint
from flask_httpauth import HTTPBasicAuth

api_blueprint = Blueprint('api', __name__, url_prefix='/api/')
auth = HTTPBasicAuth()
