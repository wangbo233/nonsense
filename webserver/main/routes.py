from flask import  Blueprint,render_template, url_for, request

main = Blueprint('main',__name__)

@main.route('/')
def index():
    print(request.url)
    return render_template("index.html")