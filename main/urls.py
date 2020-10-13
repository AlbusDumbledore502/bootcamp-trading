from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('home/', HomeView.as_view(), name="home"),
    path('register/', SignUpView.as_view(), name="sign_up"),
    path('logout/', LogoutView.as_view(), name="logout"),
]
