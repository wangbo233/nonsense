from flask import current_app
from webserver import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 关系表,除了外键没有任何其他数据，所以没有声明为模型
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # user_id作为外键实现关联
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Post:{self.title}"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String(128))
    hobbies = db.Column(db.Text)
    favourite_music = db.Column(db.Text)
    favourite_tv = db.Column(db.Text)
    favourite_book = db.Column(db.Text)
    favourite_movies = db.Column(db.Text)
    other_activities = db.Column(db.Text)
    posts = db.relationship('Blog', backref=db.backref('author', lazy=True))

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