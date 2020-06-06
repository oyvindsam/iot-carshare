class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-very-secret-key'
    SECRET_KEY = 'flask-very-secret-key'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:?cache=shared'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True


class ProductionConfig(Config):
    HOST = "34.71.196.78"
    USER = "root"
    PASSWORD = "root1234"
    DATABASE = "hireCar"

    SQLALCHEMY_DATABASE_URI = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
