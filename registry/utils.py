from datetime import datetime
from flask import request

from registry.auth import AuthUser, AuthUserLog

def log_access(person_uri, path):
    auth_user = AuthUser.objects.get(person_uri=person_uri)
    user_log = AuthUserLog()
    user_log.user = auth_user
    user_log.action = 'accessed %s' % path
    user_log.occured_at = datetime.now()
    user_log.client = request.oauth.client
    user_log.save()

def log_traceback(logger, ex, ex_traceback=None):
    import traceback
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    logger.info(tb_lines)
