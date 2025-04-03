"""
URL configuration for django_voice_search project.

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
from django.urls import path
from .views import index, text_search, voice_search,login_view, index_view

urlpatterns = [
    path("", login_view, name="login"),
    path("index/", index_view, name="index"),
    path('search/', text_search, name='text_search'),
    path('voice/', voice_search, name='voice_search'),
]
