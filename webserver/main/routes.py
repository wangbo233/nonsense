from flask import Blueprint, render_template,  request, current_app, url_for

main = Blueprint('main',__name__)


@main.route('/')
def index():
    conn = current_app.redis
    page_key = "page:cache"+str(hash(url_for('main.index')))
    content = conn.get(page_key)
    if not content:
        content = render_template("index.html")
        conn.setex(page_key, 300, content)
    return content