from rest_framework.serializers import ModelSerializer
from products.models import Products
from products.models import Category


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Products
        fields = ('id', 'title', 'description', 'about_product', 'quantity', 'article', 'price', 'size',
                  'image', 'category', 'is_active')
        read_only_fields = ('article', 'stripe_product_price_id', 'created_at', 'updated_at', )


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'description', )

