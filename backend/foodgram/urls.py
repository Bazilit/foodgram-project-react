from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from foodgram.yasg import urlpatterns as api_doc

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
urlpatterns += api_doc
