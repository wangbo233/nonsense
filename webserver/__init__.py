import os
from redis import Redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from webserver.config import Config

mail = Mail()
db = SQLAlchemy()
migrate = Migrate(db)
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"
    mail.init_app(app)
    '''
    为了解决循环引用问题,在这里引入
    '''
    from webserver.users.routes import users
    from webserver.blogs.routes import blogs
    from webserver.main.routes import main
    from webserver.api import api_bp
    app.register_blueprint(users)
    app.register_blueprint(blogs)
    app.register_blueprint(main)
    app.register_blueprint(api_bp, url_prefix='/api')

    app.redis = Redis.from_url(app.config['REDIS_URL'])

    return app
