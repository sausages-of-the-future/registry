import uuid
import urllib.request, urllib.parse, urllib.error
import hashlib
from flask import request
from flask.ext.login import current_user
from registry import app, oauth, login_manager
from mongoengine import DoesNotExist, Document, StringField, BooleanField, URLField, ReferenceField, signals, DateTimeField
from datetime import datetime, timedelta

#Flask-OAuthLib functions
@login_manager.user_loader
def load_user(user_id):
    try:
        return AuthUser.objects.get(id=user_id)
    except DoesNotExist:
        return None

@oauth.clientgetter
def load_client(client_id):
    try:
        return AuthClient.objects.get(client_id=client_id)
    except DoesNotExist:
        return None

@oauth.grantgetter
def load_grant(client_id, code):
    try:
      client = AuthClient.objects.get(client_id=client_id)
      grant = AuthGrant.objects(client=client, code=code)[0]
      #grant.user = None # OAuth2Provider expects a user
      return grant
    except DoesNotExist:
      return None

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):

    client = load_client(client_id)
    user = AuthUser.objects.get(id=current_user.get_id())

    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = AuthGrant()
    grant.client = client
    grant.code = code['code']
    grant.user = user
    grant.redirect_uri=request.redirect_uri
    grant._scopes=' '.join(request.scopes)
    grant.expires=expires
    grant.save()

    return grant

@oauth.usergetter
def get_user(username, password, *args, **kwargs):
    #todo: fix
    return AuthUser.objects.all()[0]

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    token = None
    if access_token:
        token = AuthToken.objects(access_token=access_token).first()
    elif refresh_token:
        token = AuthToken.objects(refresh_token=refresh_token).first()
    return token

@oauth.tokensetter
def save_token(token_data, request, *args, **kwargs):

    client = load_client(request.client.client_id)
    user = load_user(request.user.id) #make optional?

    # make sure that every client has only one token
    existing_tokens = AuthToken.objects(client=client)
    for token in existing_tokens:
        token.delete()

    expires_in = token_data.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    token = AuthToken()
    token.access_token = token_data['access_token']
    token.refresh_token=token_data['refresh_token']
    token.token_type = token_data['token_type']
    token.user = user
    token._scopes = urllib.parse.unquote_plus(token_data['scope'])
    token.expires=expires
    token.client = client

    token.save()

    return token

#Flask OAuthlib models
class AuthUser(Document):

    email = StringField(max_length=100, required=True, unique=True)
    password = StringField(max_length=100, required=True)
    active = BooleanField(default=True)
    person_uri = URLField()

    def is_active(self):
        #method required for flask-login
        return self.active

    def get_id(self):
        #method required for flask-login
        return str(self.id)

    def is_anonymous(self):
        #method required for flask-login
        # might need to use this for accessing public data?
        return False

    def is_authenticated(self):
        #method required for flask-login
        return True

    def set_password(self, password):
        secret_and_password = app.config['SECRET_KEY'] + password
        self.password = hashlib.md5(secret_and_password.encode('utf-8')).hexdigest()
        self.save()

    @staticmethod
    def create_user(email, password):
        user = AuthUser()
        user.email = email
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def validate_user(email, password):
        secret_and_password = app.config['SECRET_KEY'] + password
        hashed_password = hashlib.md5(secret_and_password.encode('utf-8')).hexdigest()
        try:
            user = AuthUser.objects.get(email=email.lower(), password=hashed_password)
            return user
        except DoesNotExist:
            return False

class AuthClient(Document):

    client_id = StringField(max_length=40, required=True, unique=True)
    name = StringField(max_length=55, required=True)
    description = StringField(max_length=140, required=True)
    organisation_type = StringField(max_length=140, required=False, default="central government")
    client_secret = StringField(max_length=200, required=True)
    is_confidential = BooleanField()

    _redirect_uris = StringField(required=True)
    _default_scopes = StringField(required=True)

    @staticmethod
    def register_service(name, description, scopes, redirect_uri, organisation_type):
        client = AuthClient()
        client.name = name
        client.description = description
        client.client_id = uuid.uuid4().hex
        client.client_secret = uuid.uuid4().hex
        client._default_scopes = " ".join(scopes)
        client._redirect_uris = redirect_uri
        client.service_organisation_type = organisation_type
        client.save()
        return client

    @property
    def client_type(self):

        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        redirect_uris = self.redirect_uris
        if len(redirect_uris) > 0:
            return self.redirect_uris[0]
        else:
            return None

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        client_log = AuthClientLog()
        client_log.client = document
        client_log.action = "registered"
        client_log.occured_at = datetime.now
        client_log.save()

    def validate_scopes(self, scopes):
        return True

class AuthGrant(Document):

    client = ReferenceField(AuthClient)
    user = ReferenceField(AuthUser)
    code = StringField(max_length=200, required=True)
    redirect_uri = URLField(required=True)
    expires = DateTimeField()
    _scopes = StringField()
    #
    # def validate_redirect_uri(redirect_uri):
    #     return True

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class AuthToken(Document):
    client = ReferenceField(AuthClient)
    user = ReferenceField(AuthUser)
    token_type = StringField()
    access_token = StringField(unique=True)
    refresh_token = StringField()
    expires = DateTimeField()
    _scopes = StringField()

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class AuthUserLog(Document):

    user = ReferenceField(AuthUser)
    client = ReferenceField(AuthClient)
    action = StringField(max_length=140, required=True)
    occured_at = DateTimeField(required=True)

class AuthClientLog(Document):

    client = ReferenceField(AuthClient)
    action = StringField(max_length=140, required=True)
    occured_at = DateTimeField(required=True)

signals.post_save.connect(AuthClient.post_save, sender=AuthClient)
