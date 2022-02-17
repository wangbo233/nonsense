from webserver import app,db,brcypt
from flask import Flask,render_template,redirect,flash,url_for,request,flash
from webserver.form import LoginForm,RegisterForm,BlogForm
from webserver.models import User,Blog
from flask_login import login_user,current_user,logout_user,login_required

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login',methods = ('GET','POST'))
def login():
    if current_user.is_authenticated:
        return redirect("/")
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email = login_form.email.data).first()
        if user and brcypt.check_password_hash(user.password, login_form.password.data):
            login_user(user,remember=login_form.remember.data)
            return redirect('/')
        else:
            flash("登陆信息有误，请检查您的邮箱或密码！","danger")
    return render_template('login.html',form = login_form)


@app.route('/register',methods=('GET','POST'))
def register():
    if current_user.is_authenticated:
        return redirect("/")
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/account')
@login_required
def account():
    return render_template("user-about.html")

@app.route('/blogs')
@login_required
def blogs():
    blogs = Blog.query.all()
    count = Blog.query.count()
    return render_template('blogs.html', blogs = blogs, count=count)


@app.route('/blogs/new',methods=('GET','POST'))
@login_required
def new():
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog(title = form.title.data,content = form.content.data,author=current_user)
        db.session.add(blog)
        db.session.commit()
        flash("文章已经成功发表!","success")
        return redirect('/blogs')
    return render_template('new-blog.html',form = form)


@app.route('/blogs/<int:blog_id>')
def blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('single-blog.html',title = blog.title,blog = blog)