from rest_framework import serializers, fields
from products.models import Products, Category
from django.db.models import Sum
from products.serializers import ProductSerializer
from basket.models import Basket


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    sum = fields.FloatField(required=False)
    price_all_products = fields.SerializerMethodField(required=False)
    sum_all_products = fields.SerializerMethodField(required=False)

    class Meta:
        model = Basket
        fields = ('product', 'quantity', 'sum', 'price_all_products', 'sum_all_products', 'created_timestamp')
        read_only_fields = ('created_timestamp',)

    def get_price_all_products(self, obj):
        return Basket.objects.filter(user_id=obj.user.id).price_all_products()

    def get_sum_all_products(self, obj):
        return Basket.objects.filter(user_id=obj.user.id).sum_all_products()
