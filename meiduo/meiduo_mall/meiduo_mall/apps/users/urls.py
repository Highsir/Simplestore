from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from users import views

router = DefaultRouter()
router.register(r'addresses',views.AddressViewSet,base_name='addresses')

urlpatterns = [
    url(r'^username/(?P<username>\w{5,20})/count/',views.UsernameCountView.as_view()),
    url(r'^authorizations/$',obtain_jwt_token),
    url(r'^users/$',views.CreateUserView.as_view()),
    url(r'^user/$',views.UserDetailView.as_view()),
    url(r'^email/$',views.EmailView.as_view()),
    url(r'^email/verification/$',views.VerifyEmailView.as_view()),
    url(r'^browse_histories/$',views.BrowseHistoryView.as_view()),
    url(r'^authorizations/$',views.UserAuthorizationView.as_view()),
]
urlpatterns += router.urls