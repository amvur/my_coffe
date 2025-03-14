from django.urls import path

from .views import *

urlpatterns = [
    path('', product_list, name='product_list'),
    path('create_order/', create_order, name='create_order'),
    path('edit_order/<int:order_id>/', edit_order, name='edit_order'),
    path('orders/', order_list, name='order_list'),
    path('update_order_status/<int:order_id>/<str:status>/', update_order_status, name='update_order_status'),
]