from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductModelViewSet, ProductModelViewDetail, CategoryModelViewSet, CategoryModelViewDetail, \
    BasketModelViewSet, LoginModelUserAPI, RegisterModelUserAPI, StateUserModelInTelegramBot_API, LogoutAPIView
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

app_name = 'api'
router = DefaultRouter()
router.register(r'products', ProductModelViewSet)
router.register(r'categories', CategoryModelViewSet, basename='categories')
router.register(r'baskets', BasketModelViewSet, basename='baskets')


urlpatterns = [
    path('', include(router.urls)),
    path('product-detail/<int:pk>', ProductModelViewDetail.as_view(), name='product-detail'),
    path('category-detail/<int:pk>', CategoryModelViewDetail.as_view(), name='category-detail'),
    path('registration-api/', RegisterModelUserAPI.as_view(), name='registration-api'),
    path('login-api/', LoginModelUserAPI.as_view(), name='login-api'),
    path('logout-api/', LogoutAPIView.as_view(), name='logout-api'),
    path('state-user/', StateUserModelInTelegramBot_API.as_view(), name='state-user')
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]



