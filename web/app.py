from flask import Flask

import carshare_config
import carshare_config_local
from api import jwt, api_blueprint
from api.models import db
from site_web import site_blueprint


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
    app.register_blueprint(api_blueprint, url_prefix='/api')
    jwt.init_app(app)
    app.register_blueprint(site_blueprint)

    return app


if __name__ == '__main__':
    app = create_app(carshare_config_local.DevelopmentConfig)
    app.run(host='127.0.0.1')

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
#populate_db(create_app(carshare_config.DevelopmentConfig))