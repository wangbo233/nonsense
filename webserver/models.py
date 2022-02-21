from webserver import db,login_manager,app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import  UserMixin,current_user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Follow(db.Model):
    __tablename__= 'follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    addtime = db.Column(db.DATETIME, default=datetime.now)
    
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique = True,nullable=False)
    email = db.Column(db.String(120),unique = True,nullable=False)
    password = db.Column(db.String(20),nullable=False)
    picture = db.Column(db.String(128))
    hobbies = db.Column(db.Text)
    favourite_music = db.Column(db.Text)
    favourite_tv = db.Column(db.Text)
    favourite_book = db.Column(db.Text)
    favourite_movies = db.Column(db.Text)
    other_activities = db.Column(db.Text)
    posts = db.relationship('Blog',backref=db.backref('author', lazy=True))

    #实现关注功能
    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],backref=db.backref('follower',lazy='joined'),lazy='dynamic',cascade='all,delete-orphan')
    followers = db.relationship('Follow',foreign_keys=[Follow.followed_id],backref=db.backref('followed',lazy='joined'),lazy='dynamic',cascade='all,delete-orphan')


    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.follower.filter_by(follower_id=user.id).first() is not None
    
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower_id=self.id,followed_id=user.id)
            db.session.add(f)   

    def unfollow(self,user):
        if self.is_following(user):
            f = self.followed.filter_by(followed_id=user.id)
            db.session.delete(f)   
    
    #生成一个token，用于修改密码
    def get_reset_token(self,expire_secs = 600):
        s = Serializer(app.config['SECRET_KEY'],expire_secs)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            print(user_id)
        except:
            return None
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"<User: name:{self.username} email:{self.email}>"





class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20),nullable=False)
    content = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime,nullable=False, default = datetime.utcnow)

    #user_id作为外键实现关联
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Post:{self.title}"