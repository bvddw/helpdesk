"""
URL configuration for helpdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from rest_framework.authtoken import views as rest_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', rest_views.obtain_auth_token),
    path('', views.MainView.as_view(), name='main_view'),
    path('about/', views.AboutView.as_view(), name='about_view'),
    path('', include(('user_app.urls', 'user_app'), namespace='user')),
    path('requests/', include(('help_request.urls', 'help_request'), namespace='requests')),
]
