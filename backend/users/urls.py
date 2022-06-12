from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewset
from django.urls import include, path

app_name = 'users'

router = DefaultRouter()
router.register("users", CustomUserViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]