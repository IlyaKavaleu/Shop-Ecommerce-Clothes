from django.contrib import admin
from .models import Category, Products


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', )
    fields = ('title', 'description', 'image')
    search_fields = ('title', )


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', )
    fields = ('id', 'title', 'description', 'quantity', 'article', 'size', 'price', 'stripe_product_price_id',
              'image', 'created_at', 'updated_at', 'category', 'is_active')
    readonly_fields = ('id', 'created_at', 'updated_at', 'article')
    search_fields = ('title', )


admin.site.register(Products, ProductAdmin)
admin.site.register(Category, CategoryAdmin)

