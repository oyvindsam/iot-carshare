from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

HOST = "35.228.215.119"
USER = "root"
PASSWORD = "carshare"
DATABASE = "carshare_db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
