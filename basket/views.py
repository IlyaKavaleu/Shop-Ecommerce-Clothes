from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Basket


def basket(request):
    baskets = Basket.objects.filter(user=request.user)
    context = {'baskets': baskets}
    return render(request, 'basket.html', context=context)


def basket_add(request, product_id):
    Basket.create_or_update(product_id=product_id, user=request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
