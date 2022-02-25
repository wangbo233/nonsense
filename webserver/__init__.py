import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate


app = Flask(__name__)

# 这里是URI，不是URL！！！
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
app.config["SECRET_KEY"] = "jdiah-9?lq-wdcq>"
app.config["MAIL_SERVER"] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '13379304436@163.com'
app.config['MAIL_PASSWORD'] = 'TTVGOMFVBXFMMVGE'

mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = "users.login"

REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'



from webserver.users.routes import users
from webserver.blogs.routes import blogs
from webserver.main.routes import main

app.register_blueprint(users)
app.register_blueprint(blogs)
app.register_blueprint(main)
