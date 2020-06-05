from flask import Flask

import carshare_config
from api.api import api_blueprint
from api.models import db
from api.test.populate_db import populate_db
from flask_site import site


def create_app(config=None):
    """

    Args:
        config: configuration object, specifying application variables
        such as database uri.

    Returns: instanciated Flask app

    """

    app = Flask(__name__)

    # Load configuration from external file, or use production config
    if config is None:
        app.config.from_object(carshare_config.ProductionConfig)
    else:
        app.config.from_object(config)

    db.init_app(app)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(site)

    return app


# Method to drop db.
# Specify what configuration you want to use (development or production db)
def setup_clean_db(PRODUCTION_DB=False):

    if PRODUCTION_DB:
        app = create_app(carshare_config.ProductionConfig)
    else:
        app = create_app(carshare_config.DevelopmentConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()


#setup_clean_db(PRODUCTION_DB=False)

# pass in a valid app context
populate_db(create_app(carshare_config.DevelopmentConfig))