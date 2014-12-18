from flask import render_template, request, redirect, url_for, session
from flask.ext.login import login_required, login_user, logout_user, current_user

from registry import app, auth, oauth, login_manager, registers, forms
from registry.auth import AuthClient, AuthToken, AuthUser
#from mongoengine import DoesNotExist

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/choose-provider', methods=['GET', 'POST'])
def choose_provider():
    next_ = request.args.get('next', None)
    next_ = next_.replace('http', 'https')
    form = forms.ChooseProviderForm()
    return render_template('choose-provider.html', form=form, next=next_)

@app.route('/signin', methods=['GET', 'POST'])
def login():
    provider = request.args.get('provider', None)
    form = forms.LoginForm(request.form)
    failed = False
    if request.method == 'POST' and form.validate():
        user = AuthUser.validate_user(form.data['email'], form.data['password'])
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

@app.route('/service-catalogue')
def service_catalogue():
    log = auth.AuthClientLog.objects.all()
    clients = auth.AuthClient.objects.all()
    return render_template('service-catalogue.html', clients=clients, log=log)

@app.route('/registry-catalogue')
def registry_catalogue():
    registries = []
    for cls in registers.registry_classes:
        properties = []
        exclude = ('MultipleObjectsReturned', 'id', 'DoesNotExist', 'objects', 'to_dict')
        for property, value in list(vars(cls).items()):
            if property.find('_') != 0 and property not in exclude:
                properties.append(property)

        for property, value in list(vars(registers.RegisterBase).items()):
            if property.find('_') != 0 and property not in exclude:
                properties.append(property)

        registries.append({'name': cls.__name__, 'description': cls.__doc__, 'properties': properties})

    registries = sorted(registries, key=lambda k: k['name'])
    return render_template('registry-catalogue.html', registries=registries)

@app.route('/signout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/your-data', methods=['GET', 'POST'])
@login_required
def your_data():

    user = auth.AuthUser.objects.get(id=session['user_id'])
    log = auth.AuthUserLog.objects(user=user)

    if request.method == 'POST':
        token = AuthToken.objects.get(id=request.form['revoke'])
        token.delete()
        #todo: delete client if no outstanding tokens

    tokens = AuthToken.objects()
    return render_template('your-data.html', tokens=tokens, log=log)

@app.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token():
    return None

@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
@login_required
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client = AuthClient.objects.get(client_id=request.args.get('client_id'))
        kwargs['client'] = client
        return render_template('authorize.html', avaliable_scopes=registers.avaliable_scopes, **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'
