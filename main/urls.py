from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

from .views import *

urlpatterns = [
    path('', RedirectView.as_view(pattern_name="home")),
    path('home/', HomeView.as_view(), name="home"),
    path('register/', SignUpView.as_view(), name="sign_up"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('manage/users/', ManageUsersView.as_view(), name="manage_users"),
    path('manage/stocks/', ManageStocksView.as_view(), name="manage_stocks"),
    path('stock/api/', StockAPIView.as_view(), name="stock_api"),
    path('stock/user/units/api/', UserStockAPIView.as_view(), name="user_stocks"),
    path('stock/user/portfolio/api/', UserPortfolioAPIView.as_view(), name="user_portfolio"),
    path('stock/buy/api/', BuyStocksAPIView.as_view(), name="buy_stocks"),
    path('stock/sell/api/', SellStocksAPIView.as_view(), name="sell_stocks"),
]
