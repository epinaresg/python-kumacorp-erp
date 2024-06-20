from django.urls import path, include

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/core/', include('core.urls')),
]
