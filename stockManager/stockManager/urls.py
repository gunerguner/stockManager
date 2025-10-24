"""stockManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import: from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, re_path, path

urlpatterns = [
    re_path(r'^api/', include('backend.urls')),
    path('sys/admin', admin.site.urls),
    # favicon.ico 由 Django 静态文件系统自动处理（/static/favicon.ico）
    re_path(r'^', TemplateView.as_view(template_name="index.html")),
    re_path(r'^user/', TemplateView.as_view(template_name="index.html")),
   
]
