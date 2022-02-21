from flask import Flask,render_template,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

#这里是URI，不是URL！！！
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
app.config["SECRET_KEY"] = "jdiah-9?lq-wdcq>"
app.config["MAIL_SERVER"]  = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '13379304436@163.com'
app.config['MAIL_PASSWORD'] = 'TTVGOMFVBXFMMVGE'

mail = Mail(app)


db = SQLAlchemy(app)

brcypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = "login"