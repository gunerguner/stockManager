from django.contrib import admin

# Register your models here.
from .models import Operation,Info,StockMeta

admin.site.register(Operation)
admin.site.register(Info)
admin.site.register(StockMeta)