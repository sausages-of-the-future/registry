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
app.config.from_object(os.environ.get('SETTINGS'))

#database
db = MongoEngine(app)

#logger = logging.getLogger('flask_oauthlib')
#fh = logging.FileHandler('flask.log')
#fh.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#logger.addHandler(fh)
#logger.addHandler(ch)
#app.logger.addHandler(fh)
#app.logger.addHandler(ch)


#login
login_manager = LoginManager(app)
login_manager.login_view = "login"

#api
api = restful.Api(app)
api.decorators=[cors.crossdomain(origin='*', headers = "origin,content-type,accept,authorization")]

#oauth
oauth = OAuth2Provider(app)

from registry import resources
from registry import views
from registry import auth
