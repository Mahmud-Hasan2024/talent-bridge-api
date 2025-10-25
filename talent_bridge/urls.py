"""
URL configuration for talent_bridge project.

This file defines routes for:
- Admin panel
- API root
- Swagger & Redoc documentation
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.shortcuts import redirect

# --- Swagger schema configuration ---
schema_view = get_schema_view(
    openapi.Info(
        title="Talent Bridge API",
        default_version='v1',
        description="Comprehensive API documentation for the Talent Bridge project.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@talentbridge.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# --- API root redirect (to DRF's root view) ---
def api_root_view(request):
    return redirect('api-root')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root_view, name='home'),
    path('api/v1/', include('api.urls'), name='api-root'),

    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
