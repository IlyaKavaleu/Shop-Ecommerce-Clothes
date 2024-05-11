from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Basket
from django.core.cache import cache


def basket(request):
    context = {}
    baskets = cache.get('baskets')
    if not baskets:
        context[baskets] = Basket.objects.filter(user=request.user)
        cache.set('baskets', baskets, 10)
    else:
        context['baskets'] = baskets
    return render(request, 'basket.html', context=context)


def basket_add(request, product_id):
    Basket.create_or_update(product_id=product_id, user=request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
