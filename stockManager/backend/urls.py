from django.urls import path

from . import stockViews
from . import userViews

urlpatterns = [
    path('', stockViews.show_stocks, name='index'),
    path('divident', stockViews.refresh_divident, name='divident'),
  
    path('currentUser', userViews.currentUser, name='currentUser'),
    path('login', userViews.login, name='login'),
    path('logout', userViews.logout, name='logout'),

]