"""
URL configuration for principal360_survey project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django's built-in admin (for superuser management)
    path('', RedirectView.as_view(url='/admin/', permanent=False)),  # Redirect root to custom admin
    path('', include('survey.urls')),  # Include survey app URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)