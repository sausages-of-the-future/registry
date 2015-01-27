from wtforms import Form, TextField, PasswordField, RadioField, validators
from wtforms.fields import html5

class LoginForm(Form):
    email = html5.EmailField('Email', [validators.Required(message="Enter a valid email"), validators.Email(message="Enter a valid email")])
    password = PasswordField('Password', [validators.Required(message="Enter your password")])
    twofactor = TextField('Security key <i class="fa fa-key"></i>', [validators.Required(message="Use your security key")])

class ChooseProviderForm(Form):
    provider = RadioField('Choose provider', choices=[('vouch', 'Vouch me'), ('idat', 'IDAT')])
