import os
import glob
from datetime import datetime
import hashlib
from register import app
from mongoengine import StringField, PolygonField, DateTimeField, PointField, StringField, DictField, DynamicDocument, Document, ObjectIdField, BooleanField, URLField, ListField, ReferenceField
from mongoengine import signals
from mongoengine import DoesNotExist
import hashlib
from mongoengine import signals
import uuid

avaliable_scopes = {'person:view': 'Permission to person ID and date of birth',}

#Auth stuff
class AuthUser(Document):

    email = StringField(max_length=100, required=True, unique=True)
    password = StringField(max_length=100, required=True)
    person_uri = URLField()

    @staticmethod
    def create_user(email, password):
        user = AuthUser()
        user.email = email
        user.password = hashlib.md5(app.config['SECRET_KEY'] + password).hexdigest()
        user.save()
        return user

    @staticmethod
    def validate_user(email, password):
        hashed_password = hashlib.md5(app.config['SECRET_KEY'] + password).hexdigest()
        try:
            user = AuthUser.objects.get(email=email, password=hashed_password)
            return user
        except DoesNotExist:
            return False

class AuthClient(Document):
    client_id = StringField(max_length=40, required=True, unique=True)
    name = StringField(max_length=55, required=True)
    description = StringField(max_length=140, required=True)
    client_secret = StringField(max_length=200, required=True)
    is_confidential = BooleanField()

    _redirect_uris = StringField(required=True)
    _default_scopes = StringField(required=True)

    @staticmethod
    def register_service(name, description, scopes, redirect_uri):
        client = AuthClient()
        client.name = name
        client.description = description
        client.client_id = uuid.uuid4().hex
        client.client_secret = uuid.uuid4().hex
        client._default_scopes = ",".join(scopes)
        client._redirect_uris = redirect_uri
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
    token_type = StringField()
    access_token = StringField(unique=True)
    refresh_token = StringField()
    expires = DateTimeField()
    _scopes = StringField()

    @property
    def user(self):
        return None

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

#Registers
class Person(DynamicDocument):
    """
    A list of people and their dates of birth.
    """
    born_at = DateTimeField()

    @property
    def uri(self):
        return "%s/people/%s" % (app.config['BASE_URL'], str(self.id))

    def to_dict(self):
        return {'id': str(self.id), 'born_at': self.occured_at.isoformat()}


registry_classes = [Person,]

signals.post_save.connect(AuthClient.post_save, sender=AuthClient)
