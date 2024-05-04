from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('order_create/', views.OrderCreateView.as_view(), name='order_create'),
    path('order_success/', views.SuccessTemplateView.as_view(), name='order_success'),
    path('order_canceled/', views.CanceledTemplateView.as_view(), name='order_canceled'),
    path('orders_list/', views.OrderListView.as_view(), name='orders_list'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order'),
]
