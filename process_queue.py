from redis import Redis
from webserver.users.utils import process_send_reset_email_via_queue
from app import app
import os


if __name__ == '__main__':
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    conn = Redis.from_url(REDIS_URL)
    # 这里的上下文一直使用localhost, 需啊在邮件传递时指明request.root_url
    with app.app_context(), app.test_request_context():
        process_send_reset_email_via_queue(conn)

