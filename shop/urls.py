from django.urls import path
from .views import register, login, activate, profile
from .views import home
app_name = 'shop'

urlpatterns = [
    path('', home, name='home'),
    path('shop/register.html', register, name='register'),
    path('shop/login.html', login, name='login'),
    path('shop/profile.html', profile, name='profile'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
  ]
