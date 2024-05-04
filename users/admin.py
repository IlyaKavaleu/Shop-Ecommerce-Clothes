from django.contrib import admin
from .models import MyUser, StateUserInTelegramBot


class MyUserAdmin(admin.ModelAdmin):
    fields = ('first_name', 'last_name', 'username', 'age', 'email', 'image')


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(StateUserInTelegramBot)
