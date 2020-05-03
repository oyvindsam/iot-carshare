from flask import Flask

from api.api import api
from api.models import db

app = Flask(__name__)

HOST = "35.228.215.119"
USER = "root"
PASSWORD = "carshare"
DATABASE = "carshare_db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(api)
