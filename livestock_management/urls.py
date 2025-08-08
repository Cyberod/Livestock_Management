"""
URL configuration for livestock_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from core.views import dashboard
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import api_views

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
   openapi.Info(
      title="Livestock Management API",
      default_version='v1',
      description="Decision support system API for small-scale livestock farmers",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="admin@livestockmanagement.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),
    path('', include('django.contrib.auth.urls')),
    path('', include('accounts.urls')),
    
    # Core module APIs
    path('', include('core.urls')),
    
    # API Endpoints
    path('api/health/', api_views.api_health, name='api-health'),
    path('api/system-info/', api_views.system_info, name='api-system-info'),
    
    # API Documentation
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
