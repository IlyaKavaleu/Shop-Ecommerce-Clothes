from celery import shared_task
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from .models import MyUser


@shared_task
def registration_email(username, email):
    # current_site = get_current_site(request)
    subject = 'Подтверждение регистрации'
    message = (f'Здравствуйте, {username}!\n\nДля завершения регистрации на сайте '
               f' перейдите по следующей ссылке:\n\n/users/confirm-registration/')
    send_mail(subject, message, 'kavaleuilia@gmail.com', [email])


@shared_task
def email_after_login(username, email):
    # current_site = get_current_site(request)
    # subject = f'Добро пожаловать в {current_site}.'
    subject = f'Добро пожаловать в Myshop'

    message = (
        f'Здравствуйте, {username}!\n\n'
        # f'Мы рады видеть вас снова на сайте {current_site.domain}.\n'
        f'Вы успешно вошли в свой аккаунт.\n'
        f'Надеемся, что ваше пребывание будет приятным и вы найдете все необходимые товары.\n\n'
        f'С уважением,\n'
        f'Команда Myshop'
    )
    send_mail(subject, message, 'kavaleuilia@gmail.com', [email])