import os
class Config(object):
    DEBUG = False

    SECRET_KEY = os.environ['SECRET_KEY']
    BASE_URL = os.environ['BASE_URL']
    ACCESS_CONTROL_ALLOW_ORIGIN = '*'
    OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = 7776000
    MONGODB_SETTINGS = {'DB': "betagov-registers"}

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True
