from flask_oauthlib.provider import OAuth2Provider
from models import AuthClient, AuthGrant, AuthToken, AuthUser
from register import oauth
from mongoengine import DoesNotExist
from datetime import datetime, timedelta
from functools import wraps
from flask import request
import urllib

scopes = {'person:view': 'View person and date of birth',}

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
      grant.user = None # OAuth2Provider expects a user
      return grant
    except DoesNotExist:
      return None

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):

    client = load_client(client_id)

    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = AuthGrant()
    grant.client = client
    grant.code = code['code']
    grant.redirect_uri=request.redirect_uri
    grant._scopes=' '.join(request.scopes)
    grant.expires=expires
    grant.save()

    return grant

@oauth.usergetter
def get_user(username, password, *args, **kwargs):
    return AuthUser.objects.all()[0]

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return AuthToken.objects(access_token=access_token)[0]
    elif refresh_token:
        return AuthToken.objects(refresh_token=refresh_token)[0]

@oauth.tokensetter
def save_token(token_data, request, *args, **kwargs):

    client = load_client(request.client.client_id)

    # make sure that every client has only one token
    existing_tokens = AuthToken.objects(client=client)
    for token in existing_tokens:
        token.delete()

    expires_in = token_data.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    token = AuthToken()
    token.access_token = token_data['access_token']
    #token.refresh_token=token_data['refresh_token']
    token.token_type = token_data['token_type']
    token._scopes = urllib.unquote_plus(token_data['scope'])
    token.expires=expires
    token.client = client

    token.save()

    return token
