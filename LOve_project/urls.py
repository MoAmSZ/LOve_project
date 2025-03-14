"""
URL configuration for LOve_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/logout/', LogoutView.as_view(template_name='registration/logout.html'), name='logout_confirm'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('pwa.urls')),
    path('', include('love_points.urls')),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('serviceworker.js', serve, {
        'path': 'serviceworker.js',
        'document_root': os.path.dirname(os.path.dirname(__file__)),
        'headers': {
            'Service-Worker-Allowed': '/',
            'Content-Type': 'application/javascript',
        }
    }),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
