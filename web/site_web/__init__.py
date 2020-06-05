from flask import Blueprint

site_blueprint = Blueprint("site", __name__)

from . import flask_site, site_error, site_login