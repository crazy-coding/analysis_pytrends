from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = routers.SimpleRouter()
# router.register(r'user', views.UserViewSet, basename='user')
# router.register(r'group', views.GroupViewSet, basename='group')
# router.register(r'register', views.RegisterViewSet, basename='register')
router.register(r'trend', views.TrendViewSet, basename='trend')
router.register(r'interest', views.InterestViewSet, basename='interest')
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'chart', views.ChartViewSet, basename='chart')



schema_view = get_swagger_view(title='Dashboard API')

urlpatterns = [
    path('swagger', schema_view),
    path('', include(router.urls)),

    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('auth-token/', obtain_auth_token)
    path('ingest', views.data_ingest)
]