from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from webserver.models import User
from webserver.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


# 与Flask-HTTPAuth集成，提供检查用户名和密码的函数
@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    print(user)
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


# 在认证失败的情况下返回错误响应
@basic_auth.error_handler
def basic_auth_error():
    # 401是未授权错误
    return error_response(401)


@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    return error_response(401)
