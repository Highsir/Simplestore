from django.conf.urls import url

from carts import views

urlpatterns = [
    url(r'^carts/$',views.CartView.as_view()),
    url(r'^cart/selection/$',views.CartSelectAllView.as_view()),
]