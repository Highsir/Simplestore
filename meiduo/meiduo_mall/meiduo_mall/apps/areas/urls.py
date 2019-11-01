from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas import views

# urlpatterns = [
#     url(r'^areas/$',views.AreaProvinceView.as_view()),
#     url(r'^areas/(?P<pk>\d+)/$',views.SubAreaView.as_view()),
# ]
router = DefaultRouter()
router.register(r'areas',views.AreaViewSet,base_name='areas')
urlpatterns = []
urlpatterns += router.urls




