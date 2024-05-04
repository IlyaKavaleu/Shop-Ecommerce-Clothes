import time

import requests
from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, RetrieveAPIView, \
    GenericAPIView, get_object_or_404, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from products.serializers import ProductSerializer, Products, CategorySerializer, Category
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from basket.models import Basket
from basket.serializers import BasketSerializer
from users.models import MyUser, StateUserInTelegramBot
from users.serializers import UserSerializer, StateUserModelInTelegramBotSerializer
from users.views import registration_email, email_after_login

from django.http import FileResponse
import os


class ProductModelViewSet(ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer


class ProductModelViewDetail(DestroyAPIView, UpdateAPIView, RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CategoryModelViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryModelViewDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        related_products = instance.products.all()  # Получаю все продукты связанные с данной категорией
        products_serializer = ProductSerializer(related_products, many=True)
        response_data = {
            'category': serializer.data,
            'products': products_serializer.data
        }
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.products.all().delete()
        return super().destroy(request, *args, **kwargs)


class StateUserModelInTelegramBot_API(ListAPIView, CreateAPIView):
    queryset = StateUserInTelegramBot.objects.all()
    serializer_class = StateUserModelInTelegramBotSerializer

    def post(self, request, *args, **kwargs):
        state_user = request.data.get('STATE_USER')
        user_id = request.data.get('user')
        user = MyUser.objects.get(id=user_id)
        StateUserInTelegramBot.objects.update_or_create(
            user=user,
            defaults={'STATE_USER': state_user},
        )
        return Response({})


class BasketModelViewSet(ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    pagination_class = None

    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        queryset = super().get_queryset()
        if user_id:
            queryset = queryset.filter(user=user_id)
        return queryset

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        products = Products.objects.filter(id=product_id)
        if not products.exists():
            return Response({'product_id': 'Этот объект не существует!'}, status=status.HTTP_400_BAD_REQUEST)

        obj, is_created = Basket.create_or_update(products.first().id, self.request.user)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegisterModelUserAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            try:
                user = MyUser.objects.filter(email=serializer.data.get('email')).first()
                image_default_path = 'D:\\myshop\\shop\\static\\images\\default_avatar\\default_avatar.jpg'
                userdata = {}
                if user:
                    userdata_dict = {
                        'id': user.id,
                        'user_name': 'Укажите имя пользователя' if not user.username else user.username,
                        'first_name': 'Укажите имя' if not user.first_name else user.first_name,
                        'last_name': 'Укажите фамилию' if not user.last_name else user.last_name,
                        'age': 'Укажите возраст' if not user.age else user.age,
                        'email': 'Укажите имайл' if not user.email else user.email,
                        'image': user.image.path if user.image and os.path.exists(user.image.path) else image_default_path,
                    }
                    userdata.update(userdata_dict)
                ''' for get ID new user'''
                registration_email(request, serializer.data.get('username'), serializer.data.get('email'))
                return Response({'userdata': userdata}, status=status.HTTP_201_CREATED)
            except Exception:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginModelUserAPI(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            user = authenticate(username=email, password=password)
            image_default_path = 'D:\\myshop\\shop\\static\\images\\default_avatar\\default_avatar.jpg'
            if user:
                userdata = {
                    'id': user.id,
                    'user_name': 'Укажите имя пользователя' if not user.username else user.username,
                    'first_name': 'Укажите имя' if not user.first_name else user.first_name,
                    'last_name': 'Укажите фамилию' if not user.last_name else user.last_name,
                    'age': 'Укажите возраст' if not user.age else user.age,
                    'email': 'Укажите имайл' if not user.email else user.email,
                    'image': user.image.path if user.image and os.path.exists(user.image.path) else image_default_path,
                }
                email_after_login(request, username=user.username, email=email)
                return Response({'message': 'Login successful', 'userdata': userdata}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAPIView(CreateAPIView, UpdateAPIView):
    def patch(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        try:
            user_state = StateUserInTelegramBot.objects.get(user=user_id)
            user_state.STATE_USER = False
            user_state.save()
            return Response({'message': 'Пользователь успешно вышел из системы.'}, status=status.HTTP_200_OK)
        except StateUserInTelegramBot.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)


