from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from goods import views
router = DefaultRouter()
router.register('skus/search',views.SKUSearchViewSet,base_name='skus_search')
urlpatterns = [

    # 列表界面面包屑导航
    url(r'^categories/(?P<pk>\d+)/$', views.CategoryView.as_view()),
    # 查询商品列表数据
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView1.as_view()),
    # 查询商品列表数据: 实现方式2
    url(r'^skus/$', views.SKUListView2.as_view()),

]
urlpatterns += router.urls