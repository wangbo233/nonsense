from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 一定要在这里引入，否则会404
from webserver.api import users
from webserver.api import tokens
