from wtforms import Form, TextField, PasswordField, RadioField, validators

class LoginForm(Form):
    email = TextField('Email', [validators.Required(message="Enter a valid email"), validators.Email(message="Enter a valid email")])
    password = PasswordField('Password', [validators.Required(message="Enter your password")])
    twofactor = TextField('Security key', [validators.Required(message="Use your security key")])

class ChooseProviderForm(Form):
    provider = RadioField('Choose provider', choices=[('vouch', 'Vouch me'), ('idat', 'IDAT')])
