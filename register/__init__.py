import os
import logging
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext import restful
from flask_oauthlib.provider import OAuth2Provider
from flask_restful.utils import cors
from flask_login import LoginManager 

#app
app = Flask(__name__)
app.config.from_object('config')

#database
db = MongoEngine(app)

#login
login_manager = LoginManager(app)
login_manager.login_view = "login"

#api
api = restful.Api(app)
api.decorators=[cors.crossdomain(origin='*', headers = "origin,content-type,accept,authorization")]

#oauth
oauth = OAuth2Provider(app)

from register import resources
from register import views
from register import auth
