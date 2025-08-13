from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view'),
    path('add/<int:product_id>/', views.add_to_cart, name='add'),
    path('add/', views.add_to_cart, name='add'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_by_id'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove'),
    path('update/<int:item_id>/', views.update_quantity, name='update_quantity'),
]