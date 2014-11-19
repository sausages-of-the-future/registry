from wtforms import Form, TextField, PasswordField, validators

class LoginForm(Form):
    email = TextField('Email', [validators.Required(message="Enter a valid email"), validators.Email(message="Enter a valid email")])
    password = PasswordField('Password', [validators.Required(message="Enter your password")])
