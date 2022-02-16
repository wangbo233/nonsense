from webserver.models import User,Post
from webserver import db

db.create_all()
user = User(username = "wangbo",email = "wangbo@qq.com",password = "password")
post = Post(title = "title",content = "content",user_id = 1)
db.session.add(user)
db.session.add(post)
db.session.commit()
print(user.posts)
print(user)
print(post)