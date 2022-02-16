from webserver import app
from flask import Flask,render_template,redirect,flash,url_for

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template('login.html')