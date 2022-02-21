from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,DateField,SelectField,BooleanField,TextAreaField,SubmitField
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
    #picture = FileField('picture',validators=[FileAllowed(["jpg","png"]))

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("该用户名已经被注册！请更换用户名！")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("该邮箱已经被注册！请使用别的邮箱！")

class UserInfoForm(FlaskForm):
    picture = FileField("上传照片",validators=[FileAllowed(["jpg","png"])])
    hobbies = StringField("My Hobbies:")
    music = StringField("Favourite Music Bands/Artists:")
    tv = StringField("Favourite TV Shows:")
    books = StringField("Favourite Books:")
    movies = StringField("Favourite Movies:")
    acts = StringField("Other Activities:")
    submit = SubmitField("提交")



class BlogForm(FlaskForm):
    title = StringField("title",validators=[DataRequired()])
    content = TextAreaField("content",validators=[DataRequired()])

class RequestRestForm(FlaskForm):
    email = StringField('email',validators=[DataRequired(message="请输入邮箱"),Email()])
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('找不到该邮箱指定的用户')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('password',validators=[DataRequired("请输入密码")])
    password_confirmation = PasswordField('password_confirmaiton',validators=[DataRequired("请再次输入您的密码"),EqualTo('password')])

