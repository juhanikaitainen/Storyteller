from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home_view, name='home-view'),
    path('users/', include('users.urls')),
    path('accounts/', include('accounts.urls')),
    path('stories/', include('stories.urls')),
    path('help/', include('helpp.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)