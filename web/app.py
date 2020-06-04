from flask import Flask

import config
from api.api import api
from api.models import db
from flask_site import site


def create_app():
    app = Flask(__name__)

    # Load configuration from external file
    app.config.from_object(config.Config)
    db.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(site)

    return app


# Method to drop db.
# Specify what configuration you want to use (development or production db)
def setup_clean_db(PRODUCTION_DB=False):
    app = create_app()

    if PRODUCTION_DB:
        app.config.from_object(config.ProductionConfig)
    else:
        app.config.from_object(config.DevelopmentConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()


setup_clean_db(PRODUCTION_DB=False)