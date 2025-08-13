from django.urls import path
from .views import register, login, activate, profile, password_reset_confirm, password_reset_request, logout
from .views import home, change_password, edit_profile, account_delete_request, account_delete_confirm
app_name = 'shop'

urlpatterns = [
    path('', home, name='home'),
    path('shop/register.html', register, name='register'),
    path('shop/login.html', login, name='login'),
    path('shop/logout.html/', logout, name='logout'),
    path('shop/profile/', profile, name='profile'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         password_reset_confirm,
         name='password_reset_confirm'),
    path('shop/profile/edit/', edit_profile, name='edit_profile'),
    path('shop/profile/change-password/', change_password, name='change_password'),
    path('shop/profile/delete/', account_delete_request, name='account_delete'),
    path('shop/profile/delete/confirm/<uidb64>/<token>/',
         account_delete_confirm,
         name='account_delete_confirm'),
    ]
