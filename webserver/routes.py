from webserver import app
from flask import Flask,render_template,redirect,flash,url_for,request
from webserver.form import LoginForm,RegisterForm

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login',methods = ('GET','POST'))
def login():
    login_form = LoginForm()
    if request.method=="POST":
        return redirect('/')
    else:
        return render_template('login.html',form = login_form)


@app.route('/register',methods=('GET','POST'))
def register():
    register_form = RegisterForm()
    if request.method=="POST" and request.form.get('first_name')=="wangbo":
        return redirect('/')
    return render_template('register.html',form = register_form)
