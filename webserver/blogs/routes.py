from flask import Blueprint, request, render_template, redirect, abort, current_app, url_for
from flask_login import login_required, current_user
from webserver.blogs.forms import BlogForm
from webserver.models import Blog, User
from webserver import db

blogs = Blueprint('blogs', __name__)


@blogs.route('/blogs')
@login_required
def all_blogs():
    page = request.args.get('page', 1, type=int)
    # 倒序排序
    blogs = Blog.query.order_by(Blog.pub_date.desc()).paginate(page=page, per_page=6)
    count = Blog.query.count()
    return render_template('blogs.html', blogs=blogs, count=count)


@blogs.route('/blogs/new', methods=('GET', 'POST'))
@login_required
def new():
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(blog)
        db.session.commit()
        # flash("文章已经成功发表!","success")
        return redirect('/blogs')
    return render_template('new-blog.html', form=form, subject="发布一篇新文章")


@blogs.route('/blogs/<int:blog_id>')
def blog(blog_id):
    #blog = Blog.query.get_or_404(blog_id)
    conn = current_app.redis
    page_key = "cache_blog_page:"+str(hash(blog_id))
    content = conn.get(page_key)
    if not content:
        blog = Blog.query.get_or_404(blog_id)
        content = render_template('single-blog.html', title=blog.title, blog=blog)
        conn.setex(page_key, 300, content)
    return content


@blogs.route('/blogs/<int:blog_id>/update', methods=['GET', 'POST'])
@login_required
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    form = BlogForm()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        # 提交更新，更新数据库，并且删除缓存中的内容
        conn = current_app.redis
        conn.delete("cache_blog_page:"+str(hash(blog_id)))
        db.session.commit()
        return redirect(url_for('blogs.blog', blog_id=blog_id))
    elif request.method == "GET":
        form.title.data = blog.title
        form.content.data = blog.content
    return render_template('new-blog.html', form=form, subject="更新文章")


@blogs.route('/blogs/<int:blog_id>/delete', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    db.session.delete(blog)
    db.session.commit()
    # 删除文章后，缓存中的页面也应该删除
    current_app.redis.delete("cache_blog_page:"+str(hash(blog_id)))
    return redirect('/')


@blogs.route('/blog/<string:username>')
@login_required
def user_blogs(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    blogs = Blog.query.filter_by(author=user).order_by(Blog.pub_date.desc()).paginate(page=page, per_page=6)
    return render_template('user-blogs.html', blogs=blogs, user=user)


@blogs.route('/blog/followed_by_<string:username>')
@login_required
def followed_blog(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    blogs = user.followed_blogs().paginate()
    return render_template('blogs.html', blogs=blogs)
