from django.urls import path
from .views import register, login, activate, profile, password_reset_confirm, password_reset_request
from .views import home
app_name = 'shop'

urlpatterns = [
    path('', home, name='home'),
    path('shop/register.html', register, name='register'),
    path('shop/login.html', login, name='login'),
    path('shop/profile.html', profile, name='profile'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         password_reset_confirm,
         name='password_reset_confirm'),
  ]
