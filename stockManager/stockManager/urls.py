"""stockManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, re_path, path

urlpatterns = [
    re_path(r'^api/', include('backend.urls')),
    path('sys/admin/', admin.site.urls),
]
