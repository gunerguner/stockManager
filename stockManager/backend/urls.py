from django.urls import path
from backend.views import stock, user

urlpatterns = [
    # 股票相关接口
    path('operations', stock.operations, name='operations'),
    path('stocks', stock.stocks, name='stocks'),
    path('dividend', stock.refresh_dividend, name='dividend'),
    path('clearCache', stock.clear_cache, name='clearCache'),
    path('updateIncomeCash', stock.update_income_cash, name='updateIncomeCash'),
    path('watchlist', stock.watchlist, name='watchlist'),
    
    # 用户相关接口
    path('currentUser', user.currentUser, name='currentUser'),
    path('login', user.login, name='login'),
    path('logout', user.logout, name='logout'),
]