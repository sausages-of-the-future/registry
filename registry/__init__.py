import os
import logging
from flask import Flask, make_response, render_template
from flask.ext.mongoengine import MongoEngine
from flask.ext import restful
from flask_oauthlib.provider import OAuth2Provider
from flask_restful.utils import cors
from flask_login import LoginManager

#app
app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))

#temp
#app.config['MONGODB_SETTINGS'] = {'DB': "betagov-registers"}
#app.config['SECRET_KEY'] = "fdsfdsfdsfdsfdsfds"
#app.config['BASE_URL'] = "http://registry.gov.local"

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
login_manager.login_view = "%s/choose-provider" % app.config['BASE_URL']

#api
api = restful.Api(app)
api.decorators=[cors.crossdomain(origin='*', headers = "origin,content-type,accept,authorization")]

@api.representation('text/html')
def output_html(data, code, headers):
    template = '%s.html' % data.get('slug', 'registerbase')
    resp = make_response(render_template(template, data=data))
    for key, val in headers.items():
        resp.headers[key] = value
    return resp

#oauth
oauth = OAuth2Provider(app)

from . import resources
from . import views
from . import auth

if 'SENTRY_DSN' in os.environ:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, dsn=os.environ['SENTRY_DSN'])


from messenger import Connector
connector = Connector(app)
