from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from oauth.models import OauthQQUserModel
from oauth.serializers import QQUserSerializer
from oauth.utils import generate_encrypted_openid


class QQURLView(APIView):
    """
    提供QQ登录页面网址
    """
    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.query_params.get('next')
        if not next:
            next = '/'   # 首页
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        login_url = oauth.get_qq_url()
        return Response({'login_url':login_url})

class QQUserView(APIView):
    """用户扫码登陆的回调处理"""

    def get(self, request):
        # 提取code请求参数
        code = request.query_params.get('code')
        print("code:",code)
        if not code:
            return Response({'message': '缺少code'},
                            status=status.HTTP_400_BAD_REQUEST)
        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
            print(openid)
            # return Response({'openid': openid})
        except:
            return Response({'message': 'QQ服务异常'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # 使用openid查询该QQ用户是否在美多商城中绑定过用户
        try:
            oauth_user = OauthQQUserModel.objects.get(openid=openid)
        except OauthQQUserModel.DoesNotExist:

            # 如果openid没绑定美多商城用户，则需要进行绑定，
            # 在这里将openid返回给前端，绑定时再传递服务器
            openid = generate_encrypted_openid(openid)
            return Response({'openid':openid})
        else:
            # 到此表示登录成功，如果openid已绑定美多商城用户，直接生成JWT token，并返回
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 获取oauth_user关联的user
            user = oauth_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token':token,
                'user_id':user.id,
                'username':user.username
            })
            return response

    def post(self, request):
        """绑定openid和美多用户"""

        # 创建序列化器对象
        serializer = QQUserSerializer(data=request.data)
        # 校验请求参数
        serializer.is_valid(raise_exception=True)
        # 绑定openid和美多用户（添加一条表数据）
        user = serializer.save()

        # 到此步为止，绑定成功，生成JWT并响应，完成登录
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })
        # 保存购物车
        response = merge_cart_cookie_to_redis(request,response,user)
        return response
