import stripe
from django.db import models
from users.models import MyUser
from shop import settings
from products.models import Products


class BasketQuerySet(models.QuerySet):
    def price_all_products(self):
        return sum([basket.sum() for basket in self])

    def sum_all_products(self):
        return len([basket for basket in self])

    def quauntity_on_product(self):
        return Basket.quantity

    def stripe_products(self):
        line_items = []
        for basket in self:
            item = {
                'price': basket.product.stripe_product_price_id,
                'quantity': basket.quantity,
            }
            line_items.append(item)
        return line_items


class Basket(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    objects = BasketQuerySet.as_manager()  # use like manager objects

    def __str__(self):
        return f"Корзина для {self.user.username} | Продукт: {self.product.title}"

    def sum(self):
        return self.product.price * self.quantity

    def de_json(self):
        basket_item = {
            'product_name': self.product.title,
            'quantity': self.quantity,
            'price': float(self.product.price),
            'sum': float(self.sum())
        }
        return basket_item

    @classmethod
    def create_or_update(cls, product_id, user):
        product_id = Products.objects.get(id=product_id)
        baskets = Basket.objects.filter(user=user, product=product_id)  # if this obj not you create him
        if not baskets.exists():
            obj = Basket.objects.create(user=user, product=product_id, quantity=1)
            is_created = True
            return obj, is_created
        else:
            basket = baskets.first()
            basket.quantity += 1
            basket.save()
            is_created = False
            return basket, is_created
