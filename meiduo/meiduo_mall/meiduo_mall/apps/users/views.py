from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import mixins
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from carts.utils import merge_cart_cookie_to_redis
from goods.models import SKU
from goods.serializers import SKUSerializer
from users import serializers
from users.models import User
from users.serializers import CreateUserSerializer, AddBrowseHistorySerializer


class UsernameCountView(APIView):
    def get(self,request,username):
        print(username)
        count = User.objects.filter(username=username).count()
        context = {
            'username': username,
            'count': count
        }
        return Response(context)

class CreateUserView(CreateAPIView):
    """注册用户"""
    serializer_class = CreateUserSerializer

class UserDetailView(RetrieveAPIView):
    """用户详情"""
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

class EmailView(UpdateAPIView):
    """修改用户的邮箱字段"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerializer

    def get_object(self,*args,**kwargs):
        return self.request.user

class VerifyEmailView(APIView):
    """激活邮件"""
    def get(self,request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message':'缺少token'},status=400)
        #  验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message':'链接信息无效'},status=400)
        else:
            user.email_active = True
            user.save()
            return Response({'message':'OK'})


class AddressViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    """用户地址管理"""
    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """当前用户的地址"""
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        count = request.user.addresses.count()
        if count >= 2:
            return Response({'message':'地址个数已达到上限'},status=400)
        return super(AddressViewSet, self).create(request,*args,**kwargs)

    # 重写list方法
    def list(self, request, *args, **kwargs):
        """用户地址列表数据"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        array_data = serializer.data
        return Response({
            'user_id':request.user.id,
            'default_address_id':request.user.default_address_id,
            'limit':10,
            'addresses':serializer.data
        })

class BrowseHistoryView(APIView):
    """用户 浏览记录"""
    # 验证是否登陆
    permission_classes = [IsAuthenticated]

    def post(self,request):
        s = AddBrowseHistorySerializer(data=request.data)
        s.user = request.user   # 给序列化器对象新增user属性
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)
    def get(self,request):
        """查询用户记录"""
        # 获取user_id
        user_id = request.user.id
        # 获取可以操作redis服务器的对象
        redis_conn = get_redis_connection('history')
        # 查询出redis中用户存储的浏览记录
        sku_ids = redis_conn.lrange('history_%s' % user_id,0,-1)

        # 查询sku列表数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        # 调用序列化器实现输出:序列化器序列化操作
        serializer = SKUSerializer(sku_list,many=True)
        return Response(serializer.data)

class UserAuthorizationView(ObtainJSONWebToken):
    """用户认证"""
    def post(self, request, *args, **kwargs):
        # 调用父类方法,获取drf jwt扩展默认的认证用户处理结果
        response = super(UserAuthorizationView, self).post(request,*args,**kwargs)
        # 仿照drf jwt扩展对于用户登陆的认证方式,判断用户是否认证登陆成功
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():   # 如果登陆成功,则合并购物车
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request,response,user)
        return response

























