from webserver import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique = True,nullable=False)
    email = db.Column(db.String(120),unique = True,nullable=False)
    password = db.Column(db.String(20),nullable=False)
    posts = db.relationship('Post',backref=db.backref('authour', lazy=True))

    '''
    def __init__(self,username,email,password,posts):
        self.username = username
        self.email = email
        self.password = password
        self.posts = posts
    '''
    def __repr__(self):
        return f"<User: name:{self.username} email:{self.email}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20),nullable=False)
    content = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime,nullable=False, default = datetime.utcnow)

    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    '''
    def __init__(self,title,content):
        self.title = title
        self.content = content
    '''
    def __repr__(self):
        return f"Post:{self.title}"

