from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import CartSKUSerializer, SaveOrderSerializer


class OrderSettlementView(APIView):
    """订单结算"""
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """获取订单商品信息"""
        # 获取当前用户对象
        user = request.user
        # 获取操作redis数据库的StrictRedis对象
        redis_conn = get_redis_connection('cart')
        # 获取购物车数据(字典)
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        # 获取购物车商品选中状态(列表)
        cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
        # 过滤出勾选的商品字典数据
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        # 给每一个商品sju对象补充上count数量
        for sku in skus:
            sku.count = cart[sku.id]
        # 手动响应的字典数据
        context = {
            'freight':10.0,
            'skus':CartSKUSerializer(skus,many=True).data
        }
        return Response(context)

class SaveOrderView(CreateAPIView):
    """保存订单"""
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer




