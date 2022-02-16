from webserver import app,db,brcypt
from flask import Flask,render_template,redirect,flash,url_for,request,flash
from webserver.form import LoginForm,RegisterForm
from webserver.models import User

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login',methods = ('GET','POST'))
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash("登陆成功!",'success')
        return redirect('/')
    return render_template('login.html',form = login_form)


@app.route('/register',methods=('GET','POST'))
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
    #if request.method=="POST":
        #对密码进行加密并解码为str
        hashed_passwd = brcypt.generate_password_hash(register_form.password.data).decode('utf-8')
        #print(hashed_passwd)
        #print(register_form.email.data)
        #print(register_form.username.data)
        user = User(
            username = register_form.username.data,
            email = register_form.email.data,
            password = hashed_passwd
        )
        print(user)
        db.create_all()
        db.session.add(user)
        db.session.commit()
        flash("注册成功!",'success')
        return redirect('/login')
    return render_template('register.html',form = register_form)
