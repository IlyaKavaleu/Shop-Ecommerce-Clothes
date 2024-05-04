from django.urls import path
from .views import index, detail_category, contacts, shop, detail_product, all_products, search, search_by_price

app_name = 'products'

urlpatterns = [
    path('shop/', shop, name='shop'),
    path('shop/search_by_price/', search_by_price, name='search_by_price'),
    path('index/', index, name='index'),
    path('detail_category/<int:category_id>/', detail_category, name='detail_category'),
    path('contacts/', contacts, name='contacts'),
    path('detail_product/<int:product_id>/', detail_product, name='detail_product'),
    path('all_products/', all_products, name='all_products'),
    path('', search, name='search'),
]