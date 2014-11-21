import os
class Config(object):
    DEBUG = False

    SECRET_KEY = os.environ['SECRET_KEY']
    ACCESS_CONTROL_ALLOW_ORIGIN = os.environ['ACCESS_CONTROL_ALLOW_ORIGIN']
    OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = os.environ['OAUTH2_PROVIDER_TOKEN_EXPIRES_IN']

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True