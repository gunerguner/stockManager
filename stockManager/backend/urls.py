from django.urls import path

from . import views

urlpatterns = [
    path('', views.show_stocks, name='index'),
    # path('import', views.convert_from_excel, name='import'),
    path('divident', views.refresh_divident, name='divident'),
  
]