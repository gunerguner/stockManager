from django.urls import path

from . import stockViews
from . import userViews
from . import tempViews

urlpatterns = [
    path('', stockViews.show_stocks, name='index'),
    path('divident', stockViews.refresh_divident, name='divident'),
    path('updateOriginCash',stockViews.update_origin_cash, name='updateOriginCash'),
    path('updateIncomeCash',stockViews.update_income_cash, name='updateIncomeCash'),
    
    path('currentUser', userViews.currentUser, name='currentUser'),
    path('login', userViews.login, name='login'),
    path('logout', userViews.logout, name='logout'),

    # path('makeTag', tempViews.make_tag, name='makeTag'),
]