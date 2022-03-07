from flask import current_app, url_for
from webserver import db, login_manager, bcrypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime, timedelta
from flask_login import UserMixin
import base64
import os


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 关系表,除了外键没有任何其他数据，所以没有声明为模型
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

"""
这个mixin类需要作为父类添加到User模型中
"""


class PaginatedAPIMixin(object):
    """
    to_collection_dict()方法产生一个带有用户集合表示的字典，包括items，_meta和_links部分；
    前三个参数是Flask-SQLAlchemy查询对象，页码和每页数据数量；

    """

    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            # 链接部分包括自引用以及指向下一页和上一页的链接
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # user_id作为外键实现关联
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Post:{self.title}"


class User(db.Model, UserMixin, PaginatedAPIMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String(128))
    hobbies = db.Column(db.Text)
    favourite_music = db.Column(db.Text)
    favourite_tv = db.Column(db.Text)
    favourite_book = db.Column(db.Text)
    favourite_movies = db.Column(db.Text)
    other_activities = db.Column(db.Text)
    posts = db.relationship('Blog', backref=db.backref('author', lazy=True))

    # 用户token，用于与API交互时的身份验证
    token = db.Column(db.String(32), index=True, unique=True)
    # 用户token的过期时间
    token_expiration = db.Column(db.DateTime)
    # 声明多对多的关注关系,将User实例关联到其他User实例
    # User是关系当中的右侧实体（被关注者）
    # secondary 指定了用于该关系的关联表
    # primaryjoin 指明了通过关系表关联到左侧实体（关注者）的条件
    # secondaryjoin 指明了通过关系表关联到右侧实体（被关注者）的条件
    # backref定义了右侧实体如何访问该关系
    # lazy参数表示这个查询的执行模式，设置为动态模式的查询不会立即执行，直到被调用
    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # 是否已经关注了用户
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # 关注用户
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    # 取消关注
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # 获取关注用户的博客（包括自己的）
    def followed_blogs(self):
        followed = Blog.query.join(
            followers, (followers.c.followed_id == Blog.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Blog.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Blog.pub_date.desc())

    # 生成一个token，用于修改密码
    def get_reset_token(self, expire_secs=600):
        s = Serializer(current_app.config['SECRET_KEY'], expire_secs)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            print(user_id)
        except:
            return None
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"<User: name:{self.username} email:{self.email}>"

    def to_dict(self, include_mail=False):
        data = {
            'id': self.id,
            'username': self.username,
            'picture': self.picture,
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
            }
        }
        if include_mail:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            hashed_passwd = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            self.password = hashed_passwd
            db.session.commit()

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        # 检查当前分配的token在到期之前是否至少还剩一分钟，并且在这种情况下会返回现有的token
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        # 分配一个新的token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    # 使当前token立即失效
    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    # 将一个token作为参数传入并返回此token所属的用户
    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
