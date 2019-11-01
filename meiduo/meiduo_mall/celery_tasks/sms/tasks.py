from time import sleep

from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.sms import CCP
print(1111)
@celery_app.task(name='send_sms')
def send_sms(mobile,sms_code):
    # result = CCP().send_template_sms(mobile,[sms_code,5],1)
    # print(result)

    print('发送验证码:',sms_code)
    sleep(5)
    return sms_code