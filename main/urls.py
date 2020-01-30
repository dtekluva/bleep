"""flemmer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('post_court_rep_form/', views.post_court_rep_form, name='post_court_rep_form'),
    path('get_all_users/', views.get_all_users, name='get_all_users'),
    path('get_all_forms/', views.get_all_forms, name='get_all_forms'),
    path('post_credentials_form/', views.post_credentials_form, name='post_credentials_form')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)