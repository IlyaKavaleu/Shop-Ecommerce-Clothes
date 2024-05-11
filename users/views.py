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
from .tasks import registration_email, email_after_login


def register(request):
    if request.method == 'POST':
        form = RegisterUpForm(request.POST)
        if form.is_valid():
            username, email = form.cleaned_data.get('username'), form.cleaned_data.get('email')
            registration_email.delay(username, email)   # tasks[celery]
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


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['email'], password=request.POST['password1'])
        if user is not None:
            login(request, user)
            email_after_login.delay(request.user.username, request.user.email)  # tasks[celery]
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

