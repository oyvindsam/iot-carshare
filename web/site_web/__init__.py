from flask import Blueprint

site_blueprint = Blueprint("site", __name__)

from . import flask_site