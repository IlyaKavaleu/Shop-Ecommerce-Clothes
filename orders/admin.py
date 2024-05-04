from django.contrib import admin
from .models import Order


class AdminOrder(admin.ModelAdmin):
    fields = ('first_name', 'last_name', 'email', 'address', 'basket_history', 'created', 'status', 'initiator')
    readonly_fields = ('created', )


admin.site.register(Order, AdminOrder)
