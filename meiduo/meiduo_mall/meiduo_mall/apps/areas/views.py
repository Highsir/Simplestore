from django.shortcuts import render
from rest_framework import views, mixins
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas import serializers
from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


class AreaProvinceView(ListAPIView):
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer

class SubAreaView(RetrieveAPIView):
    queryset = Area
    serializer_class = SubAreaSerializer

class AreaViewSet(ReadOnlyModelViewSet,CacheResponseMixin):
    # 如果在配置文件中设置了分页，则影响到此类，可以设置None表示不分页
    pagination_class = None
    def get_queryset(self):
        """提供数据集"""
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()
    def get_serializer_class(self):
        """提供序列化器"""
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer

@cache_response()
class CityView(views.APIView):
    def get(self, request,*args,**kwargs):
        pass

