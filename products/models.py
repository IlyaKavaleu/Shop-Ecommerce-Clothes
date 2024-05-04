import random
import string
import stripe
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100, blank=False, verbose_name='Title')
    description = models.TextField(max_length=200, blank=True, verbose_name='Description')
    image = models.ImageField(upload_to='category/', blank=True, null=True, verbose_name='Image')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


class RandomLatinCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        kwargs.setdefault('unique', True)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = [random.randint(1, 10) for _ in range(0, 10)]
        article = ''.join(str(x) for x in value)
        setattr(model_instance, self.attname, article)
        return article


class Products(models.Model):
    title = models.CharField(max_length=100, blank=False, verbose_name='Title')
    description = models.TextField(max_length=3000, blank=False, verbose_name='Description')
    about_product = models.TextField(max_length=3000, blank=False)
    article = RandomLatinCharField(max_length=20, unique=True)
    quantity = models.IntegerField(blank=False, null=True, verbose_name='Quantity')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, verbose_name='Price')
    size = models.CharField(max_length=4)
    stripe_product_price_id = models.CharField(max_length=128, null=True, blank=True)
    image = models.ImageField(upload_to='products_clothes/', blank=True, null=True, verbose_name='Image')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Category')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.stripe_product_price_id:
            stripe_product_price = self.create_stripe_product_price()
            self.stripe_product_price_id = stripe_product_price['id']
        super(Products, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    def create_stripe_product_price(self):
        stripe_product = stripe.Product.create(name=self.title)
        stripe_product_price = stripe.Price.create(
            product=stripe_product['id'], unit_amount=round(self.price * 100), currency='pln')
        return stripe_product_price
