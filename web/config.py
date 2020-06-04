class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    HOST = "34.71.196.78"
    USER = "root"
    PASSWORD = "root1234"
    DATABASE = "hireCar"
    SQLALCHEMY_DATABASE_URI = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}" + '_test'


class ProductionConfig(Config):
    HOST = "34.71.196.78"
    USER = "root"
    PASSWORD = "root1234"
    DATABASE = "hireCar"

    SQLALCHEMY_DATABASE_URI = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
