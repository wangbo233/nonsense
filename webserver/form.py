from flask_wtf import Form
from wtforms import StringField,PasswordField,DateField,SelectField
from wtforms.validators import DataRequired,Email,EqualTo

class LoginForm(Form):
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])

class RegisterForm(Form):
    username = StringField('firstname',validators=[DataRequired()])
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    password_confirmation = PasswordField('password_confirmaiton',validators=[DataRequired(),EqualTo('passowrd')])

