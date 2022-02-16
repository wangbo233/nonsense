from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,DateField,SelectField
from wtforms.validators import DataRequired,Email,EqualTo,Length

class LoginForm(FlaskForm):
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('username',validators=[DataRequired()])
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    password_confirmation = PasswordField('password_confirmaiton',validators=[DataRequired(),EqualTo('password')])

