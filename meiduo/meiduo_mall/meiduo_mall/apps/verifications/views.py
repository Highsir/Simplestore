import logging
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms.tasks import send_sms
from meiduo_mall.libs.yuntongxun.sms import CCP
from meiduo_mall.utils.exception import logger

loggers = logging.getLogger('django')

class SMSCodeView(APIView):
    def get(self,request,mobile):
        strict_redis = get_redis_connection('sms_codes')

        # 60秒内禁止重复发送短信验证码
        send_flag = strict_redis.get('send_flag_%s' % mobile)

        if send_flag:
            return Response({'message':'发送短信过于频繁'})

        # 生成短信验证码
        import random
        sms_code = '%06d' % random.randint(0,999999)
        loggers.info('sms_code:%s' % sms_code)
        # 使用云通讯发送短信验证码
        # result = CCP().send_template_sms(mobile,[sms_code,5],1)
        # print(result)
        print("验证码:",sms_code)
        # 保存短信验证码到redis expiry
        # strict_redis.setex('sms_%s' % mobile,5*60,sms_code) # 有效期5分钟
        # strict_redis.setex('send_flag_%s' % mobile,60,1)

        # 使用selery发送短信验证码
        send_sms.delay(mobile,sms_code)

        # 获取pipeline对象
        pipeline = strict_redis.pipeline()
        pipeline.setex('sms_%s' % mobile,5*60,sms_code) # 有效期5分钟
        pipeline.setex('send_flag_%s' % mobile,60,1)
        pipeline.execute() #一次性执行多个命令
        return Response({'message':'ok'})
