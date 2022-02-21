from webserver import app,db,brcypt,mail
from flask import Flask,render_template,redirect,flash,url_for,request,abort
from webserver.form import LoginForm,RegisterForm,BlogForm,UserInfoForm,RequestRestForm,ResetPasswordForm
from webserver.models import User,Blog
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
import secrets
import os

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

def save_picture(pic):
    random_hex = secrets.token_hex(8)
    _,filename_extension = os.path.split(pic.filename)
    pic_filename = random_hex+filename_extension
    pic_path = os.path.join(app.root_path,"static/user_pictures",pic_filename)
    pic.save(pic_path)

    return pic_filename

@app.route('/profile/edit',methods = ['GET','POST'])
def edit_profile():
    form = UserInfoForm()
    if form.validate_on_submit():
        if form.picture.data:
            #这里是图片的路径
            picture_file = save_picture(form.picture.data)
            current_user.picture = picture_file
        if form.hobbies.data:
            current_user.hobbies = form.hobbies.data
        if form.tv.data:
            current_user.favourite_tv = form.tv.data
        if form.movies.data:
            current_user.favourite_movies = form.movies.data
        if form.music.data:
            current_user.favourite_music = form.music.data
        if form.acts.data:
            current_user.other_activities = form.acts.data
        if form.books.data:
            current_user.favourite_book = form.books.data
        db.session.add(current_user)
        db.session.commit()
        return redirect('/account')
    return render_template('user-info-update.html',form = form)

@app.route('/account')
def account():
    return render_template("user-about.html")

@app.route('/blogs')
@login_required
def blogs():
    page = request.args.get('page',1,type=int)
    #倒序排序
    blogs = Blog.query.order_by(Blog.pub_date.desc()).paginate(per_page = 6)
    count = Blog.query.count()
    return render_template('blogs.html', blogs = blogs, count=count)


@app.route('/user/<string:username>')
@login_required
def user_blogs(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    blogs = Blog.query.filter_by(author = user).order_by(Blog.pub_date.desc()).paginate(page=page,per_page=6)
    return render_template('user-blogs.html',blogs = blogs,user=user) 

@app.route('/users')
@login_required
def users():
    page = request.args.get('page',1,type=int)
    users = User.query.order_by(User.id).paginate(per_page=6)
    #blogs = Blog.query.filter_by(author = user)
    return render_template('users.html',users = users)

@app.route('/blogs/new',methods=('GET','POST'))
@login_required
def new():
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog(title = form.title.data,content = form.content.data,author=current_user)
        db.session.add(blog)
        db.session.commit()
        #flash("文章已经成功发表!","success")
        return redirect('/blogs')
    return render_template('new-blog.html',form=form,subject="发布一篇新文章")


@app.route('/blogs/<int:blog_id>')
def blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('single-blog.html',title = blog.title,blog =blog)

@app.route('/blogs/<int:blog_id>/update',methods = ['GET','POST'])
@login_required
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    form = BlogForm()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        db.session.commit()
        return redirect(f'/blogs/{blog.id}')
    elif request.method == "GET":
        form.title.data = blog.title
        form.content.data = blog.content
    return render_template('new-blog.html',form=form,subject = "更新文章")

@app.route('/blogs/<int:blog_id>/delete',methods = ['POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    db.session.delete(blog)
    db.session.commit()
    return redirect('/')


#发送重置密码的邮件
def send_reset_email(user):
    #为用户设置一个token
    token = user.get_reset_token()
    print(token)
    msg = Message('重置密码',sender="13379304436@163.com",recipients = [user.email])
    msg.body = f'''请点击下面的链接进行密码的重置
    {url_for('reset_token',token = token, _external = True)}
    此链接会在十分钟后失效！
    '''
    mail.send(msg)

#重置密码页面
@app.route("/reset_password",methods = ['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('/')
    form  = RequestRestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        #发送邮件
        send_reset_email(user)
        flash(f'已经将重置密码邮件发送到您的邮箱:{user.email}，请查看该邮件','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title = "邮箱重置密码",form = form)

#输入新密码的页面
@app.route("/reset_password/<token>",methods = ['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('/')
    #验证用户
    user  = User.verify_reset_token(token)
    if user is None:
        #print("user is None")
        flash("您的验证表示不正确，请重试",'warning')
        return redirect(url_for('reset_request'))
    form  = ResetPasswordForm()
    if form.validate_on_submit():
        #对密码进行加密并解码为str
        hashed_passwd = brcypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_passwd
        db.session.commit()
        flash("修改密码成功!",'success')
        return redirect('/login')
    return render_template('reset_token.html',title = "输入新密码",form = form)

