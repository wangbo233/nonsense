from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,DateField,SelectField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo,Length,ValidationError
from webserver.models import User,Post



class LoginForm(FlaskForm):
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    remember = BooleanField("remember")

class RegisterForm(FlaskForm):
    username = StringField('username',validators=[DataRequired()])
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    password_confirmation = PasswordField('password_confirmaiton',validators=[DataRequired(),EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("该用户名已经被注册！请更换用户名！")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("该邮箱已经被注册！请使用别的邮箱！")


