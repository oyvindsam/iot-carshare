from flask import Flask

from api.api import api
from api.models import db


def create_app():
    app = Flask(__name__)

    HOST = "gcloud ip adress" # UPDATE WITH YOUR OWN GCLOUD DB DETAILS
    USER = "root"
    PASSWORD = "carshare"
    DATABASE = "carshare_db"

    app.config[
        "SQLALCHEMY_DATABASE_URI"] = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(api)

    return app



def setup_clean_db(TEST_DB=True):
    app = create_app()
    HOST = "gcloud ip adress"
    USER = "root"
    PASSWORD = "carshare"
    DATABASE = "carshare_db"

    if TEST_DB:
        DATABASE += '_test'
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
    with app.app_context():
        db.drop_all()
        db.create_all()


#setup_clean_db()