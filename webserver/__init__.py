from flask import Flask,render_template,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URL"] = 'sqlite:///site.db'
db = SQLAlchemy(app)
