from flask import render_template, request, redirect, url_for, session
from register import app, oauth
import models
from models import AuthClient, AuthToken, AuthUser
from mongoengine import DoesNotExist
import auth
from decorators import admin_login_required
import forms

@app.route('/')
@admin_login_required
def hello():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def admin_login():
    form = forms.LoginForm(request.form)
    failed = False
    if request.method == 'POST' and form.validate():
        user = AuthUser.validate_user(form.data['email'], form.data['password'])
        if user:
            session['user_id'] = str(user.id)
            if request.args.get('next', False):
                return redirect(request.args['next'])
            else:    
                return redirect(url_for('hello'))
        else:
            failed = True

    return render_template('login.html', form=form, failed=failed)

@app.route('/export')
@admin_login_required
def export():
    return render_template('export.html')

@app.route('/history')
@admin_login_required
def history():
    user = models.AuthUser.objects.get(id=session['user_id'])
    log = models.AuthUserLog.objects(user=user)
    return render_template('history.html', log=log)

@app.route('/service-catalogue')
def service_catalogue():
    log = models.AuthClientLog.objects.all()
    clients = models.AuthClient.objects.all()
    return render_template('service-catalogue.html', clients=clients, log=log)

@app.route('/registry-catalogue')
def registry_catalogue():
    registries = []
    for cls in models.registry_classes:
        properties = []
        for property, value in vars(cls).iteritems():
            if property.find('_') != 0 and property not in ('MultipleObjectsReturned', 'id', 'DoesNotExist', 'objects', 'to_dict'):
                properties.append(property)
        registries.append({'name': cls.__name__, 'description': cls.__doc__, 'properties': properties})
    return render_template('registry-catalogue.html', registries=registries)

@app.route('/signout')
def admin_logout():
    session.clear()
    return redirect(url_for('hello'))

@app.route('/oauth', methods=['GET', 'POST'])
@admin_login_required
def authorized():
    if request.method == 'POST':
        token = AuthToken.objects.get(id=request.form['revoke'])
        token.delete()
        #todo: delete client if no outstanding tokens

    tokens = AuthToken.objects()
    return render_template('authorized.html', tokens=tokens)

@app.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token():
    return None

@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
@admin_login_required
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client = AuthClient.objects.get(client_id=request.args.get('client_id'))
        kwargs['client'] = client
        return render_template('authorize.html', avaliable_scopes=auth.scopes, **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'
