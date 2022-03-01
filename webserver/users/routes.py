from flask import Blueprint, request, render_template, redirect, flash, url_for, current_app
from flask_login import login_required, current_user, login_user, logout_user
from webserver import bcrypt
from webserver.users.forms import LoginForm, RegisterForm, UserInfoForm, RequestRestForm, ResetPasswordForm
from webserver.users.utils import save_picture, send_reset_email_via_queue
from webserver.models import User, db

users = Blueprint('users', __name__)


@users.route('/users')
@login_required
def _users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id).paginate(per_page=6)
    # blogs = Blog.query.filter_by(author = user)
    return render_template('users.html', users=users)


@users.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect("/")
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            current_app.redis.delete("page_cache:"+str(hash(url_for('main.index'))))
            return redirect('/')
        else:
            flash("登陆信息有误，请检查您的邮箱或密码！", "danger")
    return render_template('login.html', form=login_form)


@users.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect("/")
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        # if request.method=="POST":
        # 对密码进行加密并解码为str
        hashed_passwd = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        user = User(
            username=register_form.username.data,
            email=register_form.email.data,
            password=hashed_passwd
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功!", 'success')
        return redirect('/login')
    return render_template('register.html', form=register_form)


@users.route('/logout')
@login_required
def logout():
    current_app.redis.delete("page_cache:" + str(hash(url_for('main.index'))))
    logout_user()
    return redirect(url_for("main.index"))


@users.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UserInfoForm()
    if form.validate_on_submit():
        if form.picture.data:
            # 这里是图片的路径
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
        return redirect('user', username=user.username)
    return render_template('user-info-update.html', form=form)


# 用户的个人主页
@users.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("该用户不存在", 'info')
        return redirect(url_for('main.index'))
    return render_template("user-about.html", user=user)


# 重置密码页面
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('/')
    form = RequestRestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # 发送邮件
        # send_reset_email(user)
        print(request.host_url)
        send_reset_email_via_queue(user, current_app.redis, request.host_url)
        flash(f'已经将重置密码邮件发送到您的邮箱:{user.email}，请查看该邮件', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title="邮箱重置密码", form=form)


# 输入新密码的页面
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('/')
    # 验证用户
    user = User.verify_reset_token(token)
    if user is None:
        # print("user is None")
        flash("您的验证表示不正确，请重试", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # 对密码进行加密并解码为str
        hashed_passwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_passwd
        db.session.commit()
        flash("修改密码成功!", 'success')
        return redirect('/login')
    return render_template('reset_token.html', title="输入新密码", form=form)


@users.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('users.user'), username=user.username)
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for('users.user', username=user.username))


@users.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('users.user'), username=user.username)
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('users.user', username=username))


@users.route('/user/followed_by_<username>')
@login_required
def followed_users(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first()
    followed = user.followed.order_by(User.id).paginate(per_page=6)
    return render_template('users.html', users=followed)


@users.route('/user/followers_of_<username>')
@login_required
def followers(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first()
    followers = user.followers.order_by(User.id).paginate(per_page=6)
    return render_template('users.html', users=followers)
