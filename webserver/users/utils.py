import os, secrets
from flask_mail import Message
from flask import url_for, current_app
from webserver import mail


def save_picture(pic):
    random_hex = secrets.token_hex(8)
    _, filename_extension = os.path.split(pic.filename)
    pic_filename = random_hex + filename_extension
    pic_path = os.path.join(current_app.root_path, "static/user_pictures", pic_filename)
    pic.save(pic_path)
    return pic_filename


# 发送重置密码的邮件
def send_reset_email(user):
    # 为用户设置一个token
    token = user.get_reset_token()
    print(token)
    msg = Message('重置密码', sender="13379304436@163.com", recipients=[user.email])
    msg.body = f'''请点击下面的链接进行密码的重置
    {url_for('users.reset_token', token=token, _external=True)}
    此链接会在十分钟后失效！
    '''
    mail.send(msg)
