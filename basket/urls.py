from django.urls import path, include
from .views import basket, basket_add

app_name = 'basket'

urlpatterns = [
    path('basket_page/', basket, name='basket'),
    path('basket_add/<int:product_id>', basket_add, name='basket_add'),
]

