from django.urls import path
from .views import stock, user

urlpatterns = [
    # 股票相关接口
    path('', stock.show_stocks, name='index'),
    path('divident', stock.refresh_divident, name='divident'),
    path('updateIncomeCash', stock.update_income_cash, name='updateIncomeCash'),
    
    # 用户相关接口
    path('currentUser', user.currentUser, name='currentUser'),
    path('login', user.login, name='login'),
    path('logout', user.logout, name='logout'),
]