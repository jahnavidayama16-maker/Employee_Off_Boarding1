from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('resignations/', include('resignations.urls')),
    path('assets/', include('assets.urls')),
    path('clearance/', include('clearance.urls')),
    path('reports/', include('reports.urls')),
]

# FIX: Serve both MEDIA and STATIC files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
