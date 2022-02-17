from webserver import db,login_manager
from datetime import datetime
from flask_login import  UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique = True,nullable=False)
    email = db.Column(db.String(120),unique = True,nullable=False)
    password = db.Column(db.String(20),nullable=False)
    picture = db.Column(db.String(128))

    posts = db.relationship('Blog',backref=db.backref('author', lazy=True))

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

