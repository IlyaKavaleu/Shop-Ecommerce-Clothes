import http
import time
import tkinter as tk
from io import BytesIO
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import telebot

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()


from rest_framework import status
from api.views import ProductModelViewSet
from users.models import StateUserInTelegramBot
from telebot import types

bot = telebot.TeleBot('7172219509:AAGd-hsyPQ9DnOmEdA_9pjOImCNRJ77cQHw')
BASE_URL = 'http://127.0.0.1:8000'

_USER_DATA_DICT = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    categories_button = types.InlineKeyboardButton(text="Категории", callback_data="categories")
    products_button = types.InlineKeyboardButton(text="Все товары", callback_data="products")
    registration_button = types.InlineKeyboardButton(text="Регистрация", callback_data="registration")
    login_button = types.InlineKeyboardButton(text="Вход", callback_data="login")
    keyboard.add(categories_button, products_button, registration_button, login_button)
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=keyboard, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = """
    Список доступных команд:
    /login - Войти в аккаунт
    /registration - Зарегистрироваться
    /logout - Выйти из аккаунта
    /products - Показать все товары
    /categories - Показать категории
    /my_basket - Показать мою корзину
    /my_account - Показать мой аккаунт
    """
    bot.send_message(message.chat.id, help_message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'login':
        login_in_telegram_bot(call.message)
    elif call.data == 'registration':
        registration_in_telegram_bot(call.message)
    elif call.data == 'logout':
        logout_from_telegram_bot(call.message)
    elif call.data == "products":
        get_products(call.message)
    elif call.data == 'categories':
        get_categories(call.message)
    elif call.data == "my_basket":
        get_basket(call.message)
    elif call.data == "my_account":
        private_account_telegram(call.message, user_data=_USER_DATA_DICT)
    else:
        category_id = call.data.split("_")[1]
        get_category_detail(call.message, category_id)


@bot.message_handler(commands=['my_basket'])
def get_basket(message):
    url = f'{BASE_URL}/api/state-user/'
    response_user = requests.get(url)
    user_data = response_user.json()

    user_id = _USER_DATA_DICT.get('id')
    user_state = False

    for user in user_data:
        if user['user'] == user_id:
            if user['STATE_USER'] is True:
                user_state = True
                break

    if not user_state:
        keyboard = types.InlineKeyboardMarkup()
        login_button = types.InlineKeyboardButton(text='Войти', callback_data="login")
        keyboard.add(login_button)
        bot.send_message(message.chat.id, text="Пожалуйста, войдите в свой аккаунт.", reply_markup=keyboard)
    else:
        basket_url = f'http://127.0.0.1:8000/api/baskets/'
        response_basket = requests.get(url=basket_url, params={'user': user_id})
        if response_basket.status_code == 200:
            basket_dates = response_basket.json()
            basket_message = "*Ваша корзина:*\n\n"
            basket_items = {}
            quantity_all_products = 0
            price_all_products = 0

            for basket_data in basket_dates:
                if basket_data:
                    product_id = basket_data['product']['id']
                    title = basket_data['product']['title']
                    quantity = basket_data['quantity']
                    price = float(basket_data['product']['price'])

                    quantity_all_products += quantity
                    price_all_products += quantity * price

                    # Добавляем продукт в корзину
                    basket_items[product_id] = [title, quantity, price]

            # Собираем сообщение о корзине
            for item in basket_items.values():
                basket_message += f"Товар: *{item[0]}*\nКоличество: {item[1]}\nЦена: {item[2]}\n\n"
            basket_message += f"Итоговое количество: {quantity_all_products}, Итоговая цена: {price_all_products}"
            bot.send_message(message.chat.id, text=basket_message, parse_mode='Markdown')
        else:
            keyboard = types.InlineKeyboardMarkup()
            login_button = types.InlineKeyboardButton(text='Войти', callback_data="login")
            keyboard.add(login_button)
            bot.send_message(message.chat.id, text="Ошибка получения данных. Пожалуйста, попробуйте еще раз позже.",
                             reply_markup=keyboard)



@bot.message_handler(commands=['products'])
def get_products(message):
    products_url = f'{BASE_URL}/api/products'
    products = requests.get(url=products_url).json()
    for product in products:
        product_info = f"***{product['title']}***\n"
        product_info += f"Цена: {product['price']}\n"
        product_info += f"Описание: {product['description']}\n"
        product_info += f"Артикул: {product['article']}"
        image_url = product['image']
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            photo = BytesIO(image_response.content)
            bot.send_photo(message.chat.id, photo, caption=product_info, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, product_info)


@bot.message_handler(commands=['categories'])
def get_categories(message):
    url = 'http://127.0.0.1:8000/api/categories/'
    response = requests.get(url)
    keyboard = types.InlineKeyboardMarkup()

    categories = response.json()
    category_buttons = []
    for category in categories:
        category_button = types.InlineKeyboardButton(text=category['title'], callback_data=f"category_{category['id']}")
        category_buttons.append(category_button)
    for i in range(0, len(category_buttons), 4):
        keyboard.add(*category_buttons[i:i+4])
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=keyboard)


def get_category_detail(message, category_id):
    url = f'{BASE_URL}/api/category-detail/{category_id}'
    response = requests.get(url)
    products = response.json()
    # category_detail = f'***{products.first().category.title}***'             # REPAIR!!!!!!!!!!!!!!!!
    if products['products']:
        for product in products['products']:
            product_info = f"***{product['title']}***\n"
            product_info += f"Цена: {product['price']}$\n"
            product_info += f"Описание: {product['description']}\n"
            product_info += f"О продукте: {product['about_product']}\n"
            product_info += f"Количество: {product['quantity']}\n"
            product_info += f"Размер: {product['size']}\n"
            product_info += 'В наличии: Есть в наличии\n' if {product['is_active']} else 'Нет в наличии'
            image_path = product['image']

            image_url = f'{BASE_URL}{image_path}'  # реальный хост и порт
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_data = BytesIO(image_response.content)
                bot.send_photo(message.chat.id, image_data, caption=product_info, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, product_info)
    else:
        bot.send_message(message.chat.id, 'К сожалению по данной категории ничего не найдено!', parse_mode='Markdown')


# AUTH SECTION
@bot.message_handler(commands=['registration'])
def registration_in_telegram_bot(message):
    bot.send_message(message.chat.id, "Введите имя пользователя:")
    bot.register_next_step_handler(message, enter_email_registration_in_telegram_bot)


def enter_email_registration_in_telegram_bot(message):
    username = message.text
    bot.send_message(message.chat.id, "Введите email пользователя:")
    bot.register_next_step_handler(message, enter_password_process_username_step, username)


def enter_password_process_username_step(message, username):
    email = message.text
    bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(message, repeat_registration_process_username_step, email, username)


def repeat_registration_process_username_step(message, email, username):
    password = message.text
    bot.send_message(message.chat.id, "Повторите пароль:")
    bot.register_next_step_handler(message, registration_process_password_step, email, username, password)


def registration_process_password_step(message, email, username, password):
    password1 = message.text
    registration_url = f'{BASE_URL}/api/registration-api/'
    response = requests.post(url=registration_url,
                             data={
                                 'username': username,
                                 'email': email,
                                 'password': password,
                                 'password1': password1
                             })

    _USER_DATA_DICT.update(response.json())
    if response.status_code == 201:
        url = f'{BASE_URL}/api/state-user/'
        user_id = _USER_DATA_DICT.get('id')
        requests.post(url=url, json={'STATE_USER': True, 'user': user_id})
        keyboard = types.InlineKeyboardMarkup()
        user_button = types.InlineKeyboardButton(text='Войти', callback_data="login")
        keyboard.add(user_button)
        bot.send_message(message.chat.id,
                         text=f"Поздравляем, вы успешно зарегистрирровлись.\n\nТеперь выполните вход в систему\n\n "
                              f"Email: {email}",
                         reply_markup=keyboard)


@bot.message_handler(commands=['login'])
def login_in_telegram_bot(message):
    bot.send_message(message.chat.id, "Введите email пользователя:")
    bot.register_next_step_handler(message, process_username_step)


def process_username_step(message):
    email = message.text
    bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(message, login_process_password_step, email)


def login_process_password_step(message, email):
    password = message.text
    response = authenticate_via_api(email, password)
    if response.status_code == status.HTTP_200_OK:
        user_data = response.json().get('userdata')
        # add to GLOBAL dict
        _USER_DATA_DICT.update(user_data)

        if user_data:
            url = f'{BASE_URL}/api/state-user/'
            """ back post for save state in DB """
            user_id = user_data.get('id')
            requests.post(url=url, json={'STATE_USER': True, 'user': user_id})

            keyboard = types.InlineKeyboardMarkup()
            user_button = types.InlineKeyboardButton(text='Мой аккаунт', callback_data="my_account")
            basket_button = types.InlineKeyboardButton(text='Моя корзина', callback_data="my_basket")
            logout = types.InlineKeyboardButton(text='Выйти', callback_data="logout")
            keyboard.add(user_button)
            keyboard.add(basket_button)
            keyboard.add(logout)
            bot.send_message(message.chat.id,
                             text=f"Вход выполнен успешно.\n\n Email: {email},\n\n Password hash: {hash(password)}",
                             reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        login_button = types.InlineKeyboardButton(text='Войти', callback_data="login")
        keyboard.add(login_button)
        bot.send_message(message.chat.id, text="Неверный email или пароль. Попробуйте еще раз.", reply_markup=keyboard)


def authenticate_via_api(email, password):
    url = f'{BASE_URL}/api/login-api/'
    data = {'email': email, 'password': password}
    response = requests.post(url, data=data)
    return response


def private_account_telegram(message, user_data):
    url = f'{BASE_URL}/api/state-user/'
    response = requests.get(url)
    """ check state user auth or no """
    if response.status_code == 200:
        state_data = response.json()
        state_true = False   # for default if user is not auth
        for x in state_data:
            if x['user'] == user_data.get('id') and x['STATE_USER'] is True:
                state_true = True   # rewriting state_true
        if state_true:
            user_account = f"***Мои данные***\n\n"
            user_account += f"**Имя пользователя:** {user_data.get('user_name')}\n"
            user_account += f"**Имя:** {user_data.get('first_name').title()}\n"
            user_account += f"**Фамилия:** {user_data.get('last_name').title()}\n"
            user_account += f"**Возраст:** {user_data.get('age')}\n"
            user_account += f"**Email:** {user_data.get('email')}\n"
            image_url = user_data.get('image')
            with open(image_url, 'rb') as image_file:
                bot.send_photo(message.chat.id, image_file, caption=user_account, parse_mode='Markdown')

        else:
            keyboard = types.InlineKeyboardMarkup()
            logout_button = types.InlineKeyboardButton(text='Войти', callback_data="login")
            keyboard.add(logout_button)
            bot.send_message(message.chat.id, text="Вы не авторизованы. Пройдите аутентификацию.", reply_markup=keyboard)


@bot.message_handler(commands=['logout'])
def logout_from_telegram_bot(message):
    url = f'{BASE_URL}/api/state-user/'
    user_id = _USER_DATA_DICT.get('id')

    if user_id:
        user_states = requests.get(url=url)
        for state in user_states.json():
            if state['user'] == user_id:
                if user_id:
                    url = f'{BASE_URL}/api/logout-api/'
                    response = requests.patch(url=url, data={'user': user_id})
                    if state['STATE_USER'] is True and response.status_code == 200:
                        bot.send_message(message.chat.id, text='Вы вышли из своего аккаунта.')
                    elif state['STATE_USER'] is False:
                        bot.send_message(message.chat.id, text='Вы уже вышли из своего аккаунта.')
                    else:
                        bot.send_message(message.chat.id, text='Не удалось выйти из аккаунта. Попробуйте позже.')
                else:
                    bot.send_message(message.chat.id, text='Не удалось найти информацию о вашем аккаунте.')
    else:
        bot.send_message(message.chat.id, text='Не удалось определить ваш идентификатор пользователя.')


bot.polling(none_stop=True, interval=0)
