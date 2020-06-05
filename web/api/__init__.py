from flask import Blueprint
from flask_jwt_extended import JWTManager

api_blueprint = Blueprint('api', __name__)
jwt = JWTManager()

from . import api, auth

