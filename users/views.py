from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegisterUpForm, LoginForm, EditForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .models import MyUser

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
# from shop.settings import EMAIL_HOST_USER


def registration_email(request, username, email):
    current_site = get_current_site(request)
    subject = 'Подтверждение регистрации'
    message = (f'Здравствуйте, {username}!\n\nДля завершения регистрации на сайте {current_site.domain},'
               f' перейдите по следующей ссылке:\n\n{current_site.domain}/users/confirm-registration/')
    send_mail(subject, message, 'kavaleuilia@gmail.com', [email])


def register(request):
    if request.method == 'POST':
        form = RegisterUpForm(request.POST)
        if form.is_valid():
            username, email = form.cleaned_data.get('username'), form.cleaned_data.get('email')
            registration_email(request, username, email)
            form.save()
            return redirect('users:login_view')
    else:
        form = RegisterUpForm()
    return render(request, 'registration/register.html', {'form': form})


def profile(request, user_id):
    user = MyUser.objects.get(id=user_id)
    context = {'user': user}
    return render(request, 'registration/profile.html', context)


def edit_profile(request, user_id):
    user = MyUser.objects.get(id=user_id)

    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:profile', user.id)
    else:
        form = EditForm(instance=user)

    context = {'form': form, 'user': user}
    return render(request, 'registration/edit_profile.html', context)


def email_after_login(request, username, email):
    current_site = get_current_site(request)
    subject = f'Добро пожаловать в {current_site}.'
    message = (
        f'Здравствуйте, {username}!\n\n'
        f'Мы рады видеть вас снова на сайте {current_site.domain}.\n'
        f'Вы успешно вошли в свой аккаунт.\n'
        f'Надеемся, что ваше пребывание будет приятным и вы найдете все необходимые товары.\n\n'
        f'С уважением,\n'
        f'Команда {current_site}'
    )
    send_mail(subject, message, 'kavaleuilia@gmail.com', [email])


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['email'], password=request.POST['password1'])
        if user is not None:
            login(request, user)
            email_after_login(request, request.user.username, request.user.email)
            return redirect('products:index')
        else:
            return HttpResponse('User does not exist!')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('products:index')


def change_pass(request, user_id):
    user = MyUser.objects.get(id=user_id)
    form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Важно, чтобы пользователь оставался в системе
            return redirect('users:login_view')  # Перенаправляем на профиль пользователя после изменения пароля

    context = {'form': form}
    return render(request, 'registration/change_pass.html', context)

