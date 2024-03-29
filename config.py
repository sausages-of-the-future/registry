import os
from datetime import timedelta

class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ['SECRET_KEY']
    BASE_URL = os.environ['BASE_URL']
    ACCESS_CONTROL_ALLOW_ORIGIN = os.environ['ACCESS_CONTROL_ALLOW_ORIGIN']
    OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = int(os.environ['OAUTH2_PROVIDER_TOKEN_EXPIRES_IN'])
    MONGODB_DB = os.environ['MONGODB_DB']
    MONGODB_HOST = os.environ['MONGODB_HOST']
    WWW_BASE_URL = os.environ['WWW_BASE_URL']
    #PERMANENT_SESSION_LIFETIME = timedelta(seconds=90)
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=30000)
    REDISCLOUD_URL = os.environ['REDISCLOUD_URL']
    WWW_CLIENT_ID = os.environ['WWW_CLIENT_ID']
    WWW_CLIENT_KEY = os.environ['WWW_CLIENT_KEY']

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True
