from django.shortcuts import render

from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from goods.models import GoodsCategory, SKU
from goods.serializers import ChannelSerializer, SKUSerializer, SKUIndexSerializer


class CategoryView(GenericAPIView):
    """
    商品列表页面包屑导航
    """
    queryset = GoodsCategory.objects.all()

    def get(self,request,pk=None):
        ret = {
            'cat1':'',
            'cat2':'',
            'cat3':'',
        }
        category = self.get_object()
        if category.parent is None:
            # 当前类别为一级类别
            # 通过 频道 查询 类别：
            ret['cat1'] = ChannelSerializer(category.goodschannel_set.all()[0]).data
        elif category.goodschannel_set.count() == 0:
            ret['cat3'] = ChannelSerializer(category).data
            cat2 = category.parent
            ret['cat2'] = ChannelSerializer(cat2).data
            ret['cat1'] = ChannelSerializer(cat2.parent.goodschannel_set.all()[0]).data
        else:
            # 当前类别为二级
            ret['cat2'] = ChannelSerializer(category).data
            ret['cat1'] = ChannelSerializer(category.parent.goodschannel_set.all()[0]).data
        return Response(ret)
class SKUListView1(ListAPIView):
    """
    sku列表数据
    """
    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']	# 获取url路径中的参数
        return SKU.objects.filter(category_id=category_id, is_launched=True)  # 上架商品

    # 编写类视图
class SKUListView2(ListAPIView):
    """实现方式2: 查询商品列表数据"""
    serializer_class = SKUSerializer
    queryset = SKU.objects.filter(is_launched=True)		   # 只查询上架商品

    # 配置排序和过滤的管理类
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('create_time', 'price', 'sales')	   # 排序字段
    filter_fields = ('category_id', )  # 过滤字段

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]
    serializer_class = SKUIndexSerializer