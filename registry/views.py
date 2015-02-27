from flask import render_template, request, redirect, url_for, session
from flask.ext.login import login_required, login_user, logout_user, current_user, current_app
import dateutil.parser
from registry import app, auth, oauth, login_manager, registers, forms, locator
from registry.auth import AuthClient, AuthToken, AuthUser
#from mongoengine import DoesNotExist

from registry.utils import log_traceback

from itsdangerous import TimestampSigner
import hashlib
from time import (
    gmtime,
    mktime
)
from datetime import datetime
from uuid import uuid4

#helpers
def tokenize_name(name):
    return "%s %s." % (name.split(' ')[0], name.split(' ')[1][0])


#filters
@app.template_filter('format_scope')
def format_scope_filter(value):
    result = ''
    for k,v in registers.avaliable_scopes.items():
        if value == k:
            result = v
    return result

@app.template_filter('format_date')
def format_date_filter(value):
    date = dateutil.parser.parse(str(value))
    return date.strftime('%A %d %B')

@app.template_filter('format_date_time')
def format_date_time_filter(value):
    date = dateutil.parser.parse(str(value))
    return date.strftime('%d %B %Y - %H:%M')

@app.route('/')
def index():
    return redirect(app.config['WWW_BASE_URL'])

@app.route('/choose-provider', methods=['GET', 'POST'])
def choose_provider():

    locator.send_message({"active": "registry"})

    next_ = request.args.get('next', None)
    form = forms.ChooseProviderForm()
    return render_template('choose-provider.html', form=form, next=next_)

@app.route('/signin', methods=['GET', 'POST'])
def login():
    provider = request.args.get('provider', None)
    form = forms.LoginForm(request.form)
    failed = False
    if request.method == 'POST' and form.validate():
        user = AuthUser.validate_user(
            form.data['email'], form.data['password'])
        if user:
            login_user(user)
            if request.args.get('next', False):
                return redirect(request.args['next'])
            else:
                return redirect(url_for('index'))
        else:
            failed = True

    return render_template('login.html', form=form, failed=failed, provider=provider)

@app.route('/export')
@login_required
def export():
    return render_template('export.html')

@app.route('/history')
@login_required
def history():
    user = auth.AuthUser.objects.get(id=session['user_id'])
    log = auth.AuthUserLog.objects(user=user)
    return render_template('history.html', log=log)

@app.route('/services')
def service_catalogue():
    log = auth.AuthClientLog.objects.all()
    clients = auth.AuthClient.objects.all()
    return render_template('service-catalogue.html', clients=clients, log=log)

@app.route('/access')
def access():
    return render_template('access.html')

@app.route('/registries')
def registry_catalogue():
    registries = []
    return render_template('registry-catalogue.html', registries=registries)

@app.route('/signout')
def logout():
    logout_user()
    return redirect(url_for('your_data'))

@app.route('/your-data', methods=['GET', 'POST'])
@login_required
def your_data():

    user = auth.AuthUser.objects.get(id=session['user_id'])
    person = registers.Person.objects.get(id=user.person_uri.split("/")[-1])
    tokenized_name = tokenize_name(person.full_name)
    log = auth.AuthUserLog.objects(user=user).order_by('-occured_at')

    if request.method == 'POST':
        token = AuthToken.objects.get(id=request.form['revoke'])
        token.delete()
        # todo: delete client if no outstanding tokens

    tokens = AuthToken.objects()
    return render_template('your-data.html', tokens=tokens, log=log, tokenized_name=tokenized_name)

@app.route('/your-data/access', methods=['GET', 'POST'])
@login_required
def your_access():

    user = auth.AuthUser.objects.get(id=session['user_id'])
    person = registers.Person.objects.get(id=user.person_uri.split("/")[-1])
    tokenized_name = tokenize_name(person.full_name)
    log = auth.AuthUserLog.objects(user=user).order_by('-occured_at')

    if request.method == 'POST':
        token = AuthToken.objects.get(id=request.form['revoke'])
        token.delete()
        # todo: delete client if no outstanding tokens

    tokens = AuthToken.objects()
    return render_template('your-access.html', tokens=tokens, log=log, tokenized_name=tokenized_name)

@app.route('/your-data/log', methods=['GET', 'POST'])
@login_required
def your_log():

    user = auth.AuthUser.objects.get(id=session['user_id'])
    person = registers.Person.objects.get(id=user.person_uri.split("/")[-1])
    tokenized_name = tokenize_name(person.full_name)
    log = auth.AuthUserLog.objects(user=user).order_by('-occured_at')

    if request.method == 'POST':
        token = AuthToken.objects.get(id=request.form['revoke'])
        token.delete()
        # todo: delete client if no outstanding tokens

    tokens = AuthToken.objects()
    return render_template('your-log.html', tokens=tokens, log=log, tokenized_name=tokenized_name)

@app.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token():
    return None

@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
@login_required
def authorize(*args, **kwargs):
    if request.method == 'GET':

        locator.send_message({"active": "registry"})

        client = AuthClient.objects.get(
            client_id=request.args.get('client_id'))
        kwargs['client'] = client
        return render_template('authorize.html', avaliable_scopes=registers.avaliable_scopes, **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@app.route('/register-user', methods=['POST'])
def register_user():
    data = request.form
    if not (data['full_name'] or data['email']):
        return 'Bad Request', 404
    signed_data = request.headers['Authorisation']
    client_key = app.config['WWW_CLIENT_KEY']
    signer = TimestampSigner(client_key, digest_method=hashlib.sha256)
    try:
        unsigned = signer.unsign(signed_data, max_age=5)
        client_id, email, full_name = unsigned.decode('utf-8').split(':')
        if client_id != app.config['WWW_CLIENT_ID']:
            raise Exception
        if email != data['email']:
            raise Exception
        if full_name != data['full_name']:
            raise Exception
    except Exception as ex:
        log_traceback(current_app.logger, ex)
        return 'Unauthorized', 401

    person = registers.Person()
    person.born_at = datetime.fromtimestamp(mktime(gmtime(0)))
    person.full_name = full_name
    person.save()

    random_temp_password = uuid4().hex
    user = auth.AuthUser.create_user(email, random_temp_password)
    user.person_uri = person.uri
    user.save()

    return 'Created', 201

@app.route('/update-user-password', methods=['POST'])
def update_user_password():
    email = request.form.get('email')
    if not email:
        return 'Bad Request', 404
    signed_data = request.headers['Authorisation']
    client_key = app.config['WWW_CLIENT_KEY']
    signer = TimestampSigner(client_key, digest_method=hashlib.sha256)
    try:
        unsigned = signer.unsign(signed_data, max_age=5)
        client_id, user_email, password = unsigned.decode('utf-8').split(':')
        if client_id != app.config['WWW_CLIENT_ID']:
            raise Exception
        if email != user_email:
            raise Exception

        user = AuthUser.objects.filter(email=email).first()
        if not user:
            abort(404)
        else:
            user.set_password(password)
            user.save()
            return 'OK', 200

    except Exception as ex:
        log_traceback(current_app.logger, ex)
        return 'Unauthorized', 401
