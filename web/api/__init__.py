from flask import Blueprint
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

api_blueprint = Blueprint('api', __name__, url_prefix='/api/')
auth = HTTPTokenAuth(scheme='Bearer')
