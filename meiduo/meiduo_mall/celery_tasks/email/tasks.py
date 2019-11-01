

# 使用装饰器装饰函数,把函数变为一个celery任务
from django.core.mail import send_mail

from celery_tasks.main import celery_app

# @celery_app.task(name='send_email')
# def send_email():
#     print('send_email')
from meiduo_mall import settings
from meiduo_mall.settings import dev


@celery_app.task(name='send_email')
def send_verify_email(to_email,verify_url):
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' \
                   % (to_email, verify_url, verify_url)
    send_mail(subject, "这是邮件正文", settings.dev.EMAIL_FROM, [to_email],
              html_message=html_message)