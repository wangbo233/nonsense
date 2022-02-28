import json
import os
import secrets

from flask import current_app
from flask_mail import Message

from webserver import mail


def save_picture(pic):
    random_hex = secrets.token_hex(8)
    _, filename_extension = os.path.split(pic.filename)
    pic_filename = random_hex + filename_extension
    pic_path = os.path.join(current_app.root_path, "static/user_pictures", pic_filename)
    pic.save(pic_path)
    return pic_filename


# 把要发送邮件的信息存入redis队列
def send_reset_email_via_queue(user, conn, root_url):
    token = user.get_reset_token()
    sender = os.environ.get('EMAIL_USER')
    recipients = [user.email]
    data = {
        'token': token,
        'sender': sender,
        'recipients': recipients,
        'root_url': root_url,  # 解决app.context的上下文问题
    }
    conn.rpush("queue:email", json.dumps(data))

# 不断的查询队列，如果有邮件就发送
def process_send_reset_email_via_queue(conn):
    while True:
        email_info = conn.blpop(['queue:email'], 30)
        if not email_info:
            continue
        email_data = json.loads(email_info[1])
        send_reset_email(email_data)


# 发送重置密码的邮件的执行函数
def send_reset_email(email_data):
    token = email_data['token']
    sender = email_data['sender']
    recipients = email_data['recipients']
    root_url = email_data['root_url']
    msg = Message('重置密码', sender=sender, recipients=recipients)
    msg.body = f'''请点击下面的链接进行密码的重置
    {root_url + "reset_password/" + token}
    此链接会在十分钟后失效！
    '''
    mail.send(msg)
