from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,DateField,SelectField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,Length,ValidationError
from webserver.models import User,Blog
from flask_login import current_user



class LoginForm(FlaskForm):
    email = StringField('email',validators=[DataRequired(message="请输入邮箱"),Email()])
    password = PasswordField('password',validators=[DataRequired(message="请输入密码")])
    remember = BooleanField("remember")

class RegisterForm(FlaskForm):
    username = StringField('username',validators=[DataRequired("请输入用户名")])
    email = StringField('email',validators=[DataRequired("请输入邮箱"),Email()])
    password = PasswordField('password',validators=[DataRequired("请输入密码")])
    password_confirmation = PasswordField('password_confirmaiton',validators=[DataRequired("请再次输入您的密码"),EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("该用户名已经被注册！请更换用户名！")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("该邮箱已经被注册！请使用别的邮箱！")

class BlogForm(FlaskForm):
    title = StringField("title",validators=[DataRequired()])
    content = TextAreaField("content",validators=[DataRequired()])
