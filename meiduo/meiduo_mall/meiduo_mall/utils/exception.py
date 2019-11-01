import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger('Django')

def custom_exception_handler(exc,context):

    # 调用DRF的 exception_handler 函数处理异常，如果处理成功，会返回一个`Response`类型的对象
    response = exception_handler(exc,context)
    if response is None:
        view = context['view']
        error = '服务器内部错误： %s，%s' % (view, exc)
        logger.error(error)
        return Response({'message':error},status=500)
    return response