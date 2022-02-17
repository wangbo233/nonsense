from flask import Flask,render_template,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

#这里是URI，不是URL！！！
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
app.config["SECRET_KEY"] = "jdiah-9?lq-wdcq>"

db = SQLAlchemy(app)
brcypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = "login"