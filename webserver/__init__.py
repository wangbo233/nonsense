from flask import Flask,render_template,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)

#这里是URI，不是URL！！！
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
app.config["SECRET_KEY"] = "jdiah-9?lq-wdcq>"

db = SQLAlchemy(app)
brcypt = Bcrypt()