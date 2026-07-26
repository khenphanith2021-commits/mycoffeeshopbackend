"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse 
from django.conf import settings 
from django.conf.urls.static import static 
from django.shortcuts import redirect
from api.views import custom_login_page, custom_register_page

from api.views import custom_logout
from api.views import RegisterUserView


def home_api_status(request):
    return JsonResponse({
        "status": "online",
        "message": "Welcome to Coffee Shop API Backend!",
        "endpoints": {
            "login": "/custom-login/",
            "register": "/custom-register/",
            "admin": "/admin/",
            "api_root": "/api/",
            "status": "/status/"
        }
    })


def admin_logout_redirect(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('/custom-login/')

urlpatterns = [
    path('admin/login/', lambda request: redirect('/custom-login/')),
    path('admin/logout/', admin_logout_redirect),
    path('', custom_login_page, name='root_login'),
    path('custom-login/', custom_login_page, name='custom_login'),
    path('custom-register/', custom_register_page, name='custom_register'),
    

    path('admin/', admin.site.urls),
    path('status/', home_api_status, name='api_status'),
    path('api/logout/', custom_logout, name='custom_logout'),
    path('api/', include('api.urls')),

    path('api/register-user/', RegisterUserView.as_view(), name='register-user'),
]

# route to (Media Files)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)