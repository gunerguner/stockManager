from django.contrib import admin

# Register your models here.
from .models import Operation,Info

admin.site.register(Operation)
admin.site.register(Info)