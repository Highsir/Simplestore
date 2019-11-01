import base64
import pickle

from django.shortcuts import render

from redis.client import Pipeline
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts import constants
from carts.serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelecteAllSerilizer
from goods.models import SKU


class CartView(APIView):
    def perform_authentication(self, request):
        """
        drf框架在视图执行前会调用此方法进行身份认证(jwt认证)
        如果认证不通过,则会抛异常返回401状态码
        问题: 抛异常会导致视图无法执行
        解决: 捕获异常即可
        """
        try:
            super().perform_authentication(request)
        except Exception:
            pass

    def post(self,request):
        """
        添加购物车
        """
        # 校验请求参数是否合法
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取请求参数
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        user = request.user
        if user.is_authenticated(): # 判断是否登录
            # 用户已登陆,下redis红保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipepline()
            # 增加购物车商品数量
            pl.hincrby('cart_%s' % user.id,sku_id,count)
            if selected:    # 保存商品勾选状态
                pl.sadd('cart_selected_%s' % user.id,sku_id)
            pl.execute()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            # 1.从cookie中获取购物车信息
            cart = request.COOKIES.get('cart')
            # 2.base64字符串->字典
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            # 3.新增字典中对应的商品数量
            sku = cart.get(sku_id)
            if sku: # 原有数量+新增数量
                count += int(sku.get('count'))
                cart[sku_id] = {
                    'count':count,
                    'selected':selected
                }
            # 4.字典->base64字符串
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
            # 5.通过cookies保存购物车数据(base64字符串)
            response = Response(serializer.data,status=201)
            # 参数3:cookie 有效期
            response.set_cookie('cart', cookie_cart, constants.CART_COOKIE_EXPIRES)
            return response

    def get(self,request):
        """
        查询购物车所有的商品
        """
        user = request.user
        if user.is_authenticated():
            redis_conn = get_redis_connection('cart')
            dict_cart = redis_conn.hgetall('cart_%s' % user.id)
            list_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            cart = {}
            for sku_id,count in dict_cart.items():
                cart[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in list_cart_selected
                }
        else:
            # 用户未登录,从cookie中读取
            cart = request.COOKIES.get('cart')
            if cart is not None:
                # 购物车base64字符串 --> 字典
                cart = pickle.loads(base64.b64decode(cart.encode()))
                print('cookie:',cart)
            else:
                cart = {}
        # 查询购物车中所有的商品
        skus = SKU.objects.filter(id__in = cart.keys())
        for sku in skus:
            # 给sku对象新增两个字段: 商品数量和勾选状态
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus,many=True)
        return Response(serializer.data)

    def put(self,request):
        """修改购物车数据"""
        # 校验参数
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取校验后的参数
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        user = request.user
        if user.is_authenticated():
            # 用户已登陆,在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 修改商品数量
            pl.hset('cart_%s' % user.id,sku_id,count)
            # 修改商品的勾选状态
            if selected:
                pl.sadd('cart_selected_%s' % user.id,sku_id)
            else:
                pl.srem('cart_selected_%s' % user.id,sku_id)
            return Response(serializer.data)

        else:
            # 未登录,从coolie中获取购物车信息
            cart = request.COOKIES.get('cart')
            # base64字符串->字典
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            # 修改字典中对应商品数量和选中状态
            cart[sku_id] = {
                'count':count,
                'selected':selected
            }
            # 字典->base64字符串
            cookie_cart = base64.b64encode(pickle.dumps().decode())
            # 通过cookie保存购物车数据(bas64字符串)
            response = Response(serializer.data)
            response.set_cookie('cart',cookie_cart,constants.CART_COOKIE_EXPIRES)
            return response

    def delete(self,request):
        """删除购物车数据"""
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']

        user = request.user
        if user.is_authenticated():
            # 用户已登录，在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 用户未登录，在cookie中保存
            response = Response(status=status.HTTP_204_NO_CONTENT)
            # 1. 从cookie中获取购物车信息
            cart = request.COOKIES.get('cart')
            if cart is not None:
                # 2. base64字符串 -> 字典
                cart = pickle.loads(base64.b64decode(cart.encode()))
                # 3. 删除字典中对应的商品
                if sku_id in cart:
                    del cart[sku_id]
                    # 4. 字典 --> base64字符串
                    cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                    # 5. 通过cookie保存购物车数据（base64字符串）
                    response.set_cookie('cart', cookie_cart,
                                        constants.CART_COOKIE_EXPIRES)
                    return response

class CartSelectAllView(APIView):
    """购物车全选和全不选"""
    def perform_authentication(self, request):
        """
        drf框架在视图执行前会调用此方法进行身份认证(jwt认证)
        如果认证不通过,则会抛异常返回401状态码
        问题: 抛异常会导致视图无法执行
        解决: 捕获异常即可
        """
        try:
            super().perform_authentication(request)
        except Exception:
            pass

    def put(self,request):
        """全选或全不选"""
        serializer = CartSelecteAllSerilizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data['selected']

        user = request.user
        if user.is_authenticated():
            # 用户已登陆,在redis中保存
            redis_conn = get_redis_connection('cart')
            cart = redis_conn.hgetall('cart_%s' % user.id)
            sku_id_list = cart.keys()
            if selected:    # 全选
                redis_conn.sadd('cart_selected_%s' % user.id,*sku_id_list)
            else:   #取消全选
                redis_conn.srem('cart_selected_%s' % user.id,*sku_id_list)
            return Response({'message':'OK'})
        else:
            response = Response({'message':'OK'})
            # 从cookie中获取购物车信息
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('cart',cookie_cart,constants.CART_COOKIE_EXPIRES)
            return response





























