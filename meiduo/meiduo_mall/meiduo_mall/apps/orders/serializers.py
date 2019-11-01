from decimal import Decimal

from django.db import transaction
from django.utils.timezone import now
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品数据序列化器"""
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id','name','default_image_url','price','count')
class SaveOrderSerializer(ModelSerializer):
    """保存订单序列化器"""
    class Meta:
        model = OrderInfo
        fields = ('order_id','address','pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address':{
                'write_only':True,
                'required':True,
            },
            'pay_method':{
                'write_only':True,
                'required':True
            }
        }
    def create(self, validated_data):
        """保存订单"""
        # 获取下单用户及请求参数(地址，支付方式)
        user =self.context['request'].user
        address = validated_data.get('address')
        pay_method = validated_data.get('pay_method')
        # 生成订单编号 20180704174607000000001
        order_id = now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # todo: 订单信息表: 保存订单基本信息（新增一条订单数据）
        with transaction.atomic():  # 开启一个事务
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                order = OrderInfo.objects.create(
                    order_id = order_id,
                    user = user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal('0'),
                    freight = Decimal('10.00'),
                    pay_method = pay_method,
                    status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']  # 未支付
                    if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
                    else OrderInfo.ORDER_STATUS_ENUM['UNSEND']  # 货到付款
                )
                # 从Redis中查询购物车商品
                # cart_1 = {1: 2, 2: 2}
                # cart_selected_1 = {1, 2}
                redis_conn = get_redis_connection('cart')
                redis_cart = redis_conn.hgetall('cart_%s' % user.id)
                selected_sku_ids = redis_conn.smembers('cart_selected_%s' % user.id)
                # 过滤出勾选的购物车商品id和数量
                carts = {}
                for sku_id in selected_sku_ids:
                    carts[int(sku_id)] = int(redis_cart[sku_id])

                # 遍历勾选的商品id
                sku_ids = carts.keys()
                for sku_id in sku_ids:
                    # 查询sku对象
                    sku = SKU.objects.get(id=sku_id)
                    # 判断库存
                    sku_count = carts[sku.id]   # 购买数量
                    if sku_count > sku.stock:
                        transaction.savepoint_rollback(save_id)
                        raise serializers.ValidationError('库存不足')
                    # 修改sku表： 减少库存，增加销量
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()

                    # 修改spu表： 修改SPU销量
                    sku.goods.sales += sku_count
                    sku.goods.save()

                    # 订单商品表: 保存订单商品信息（新增多条数据）
                    OrderGoods.objects.create(
                        order = order,
                        sku = sku,
                        count = sku_count,
                        price = sku.price
                    )
                    # 累加订单商品总数量和总金额
                    order.total_count += sku_count
                    order.total_amount += (sku_count * sku.price)
                    # 修改订单总数量和总金额
                    order.total_amount += order.freight  # 加入运费
                    order.save()
            except ValidationError:
                raise # 库存不足时事务已做回滚
            except Exception as e:
                # 回滚到保存点
                transaction.savepoint_rollback(save_id)
                print('下单失败',e)
                raise
            # 提交事务
            transaction.savepoint_commit(save_id)
            # 清除购物车中已结算的商品
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id,*selected_sku_ids)
            pl.srem('cart_selected_%s' % user.id,*selected_sku_ids)
            pl.execute()
            # 返回新创建的订单对象
            return order