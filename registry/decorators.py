import traceback

from datetime import datetime
from functools import wraps
from flask import session, request, redirect, url_for, current_app

from registry.auth import AuthUserLog

def log_traceback(logger, ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    logger.info(tb_lines)

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
        except Exception as ex:
            log_traceback(current_app.logger, ex)

        return f(*args, **kwargs)
    return decorated_function


