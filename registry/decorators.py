from datetime import datetime
from functools import wraps
from flask import session, request, redirect, url_for, current_app

from registry.auth import AuthUserLog

def audit_log(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            licences = args
            user_log = AuthUserLog()
            user_log.user = request.oauth.user
            user_log.action = 'accessed %s%s' % (current_app.config['BASE_URL'], request.path)
            user_log.occured_at = datetime.now()
            user_log.client = request.oauth.client
            user_log.save()
        except RuntimeError as e:
            current_app.logger.info('error %s' % e)
        return f(*args, **kwargs)
    return decorated_function


