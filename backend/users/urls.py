from rest_framework.routers import DefaultRouter
from djoser.views import TokenDestroyView
from users.views import CustomUserViewset, CustomTokenCreateView
from django.urls import include, path

app_name = 'users'

router = DefaultRouter()
router.register("users", CustomUserViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/',
         CustomTokenCreateView.as_view(), name='login'),
    path('auth/token/logout/',
         TokenDestroyView.as_view(), name='logout'),
]