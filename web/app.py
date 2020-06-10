from flask import Flask
from flask_bootstrap import Bootstrap

from api import jwt, api_blueprint
from api.models import db
from api.test.populate_db import populate_db
from site_web import site_blueprint

# config file location. How to use: make a copy of 'carshare_config' and
# call it 'carshare_config_local', then DO NOT BACK IT UP with git.
# Then we can have our own local config files with our own settings (db path, password etc.)
# and do not have to update it every time we pull someones elses code.
# Note: sometimes you might need to add new settings from 'carshare_config'
CONFIG_FILE_PROD = 'carshare_config_local.ProductionConfig'
CONFIG_FILE_DEV = 'carshare_config_local.DevelopmentConfig'


def create_app(config=None):
    """

    Args:
        config: configuration object, specifying application variables
        such as database uri.

    Returns: instanciated Flask app

    """

    app = Flask(__name__,
                template_folder='site_web/templates',
                static_folder='site_web/static')

    # Load configuration from external file, or use production config
    if config is None:
        app.config.from_object(CONFIG_FILE_PROD)
    else:
        app.config.from_object(config)

    db.init_app(app)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    jwt.init_app(app)
    app.register_blueprint(site_blueprint)
    Bootstrap(app)

    return app


if __name__ == '__main__':
    # create app from config
    app = create_app(CONFIG_FILE_DEV)
    with app.app_context():
        populate_db(app)
    app.run(host='127.0.0.1')


# Method to drop db.
# Specify what configuration you want to use (development or production db)
def setup_clean_db(PRODUCTION_DB=False):

    if PRODUCTION_DB:
        app = create_app(CONFIG_FILE_PROD)
    else:
        app = create_app(CONFIG_FILE_DEV)

    with app.app_context():
        db.drop_all()
        db.create_all()


#setup_clean_db(PRODUCTION_DB=False)

# pass in a valid app context
#populate_db(create_app(CONFIG_FILE_DEV)