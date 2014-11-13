from wtforms import Form, BooleanField, TextField, RadioField, HiddenField, TextAreaField, validators, ValidationError, PasswordField

class LoginForm(Form):
    email = TextField('Email', [validators.Required(message="Enter a valid email"), validators.Email(message="Enter a valid email")])
    password = PasswordField('Password', [validators.Required(message="Enter your password")])

# class AuthorizeForm(Form):
#     client_name = TextField('Name', [validators.Required()])