from django.urls import path
from .views import register, login_view, logout_view, profile, edit_profile, change_pass, registration_email

app_name = 'users'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout_view'),
    path('profile/<int:user_id>', profile, name='profile'),
    path('edit_profile/<int:user_id>', edit_profile, name='edit_profile'),
    path('change_pass/<int:user_id>', change_pass, name='change_pass'),
]
