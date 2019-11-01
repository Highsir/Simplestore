from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.models import GoodsCategory, GoodsChannel, SKU
from goods.search_indexes import SKUIndex


class CategorySerializer(serializers.ModelSerializer):
    """类别序列化器"""
    class Meta:
        model = GoodsCategory
        fields = ('id','name')

class ChannelSerializer(serializers.ModelSerializer):
    """频道序列化器"""
    category = CategorySerializer
    class Meta:
        model = GoodsChannel
        fields = ('category','url')

class SKUSerializer(serializers.ModelSerializer):
    """
    序列化器输出商品sku信息
    """
    class Meta:
        # 输出:序列化字段
        model = SKU
        fields = ('id','name','price','default_image_url','comments')

class SKUIndexSerializer(HaystackSerializer):
    """SKU索引结果数据序列化器"""
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')