from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from .models import Products, Category


def index(request):
    return render(request, 'index.html')


def detail_category(request, category_id):
    context = {}
    categories = cache.get('categories')
    category = cache.get(f'category_{category_id}')
    products = cache.get(f'products_{category_id}')
    if not categories or not category or not products:
        categories = Category.objects.all()   # show all
        category = Category.objects.get(id=category_id)
        products = Products.objects.filter(category=category)

        cache.set('categories', categories, 10)
        cache.set(f'category_{category_id}', category, 10)
        cache.set(f'products_{category_id}', products, 10)\

        context['categories'] = categories
        context['category'] = category
        context['products'] = products
    else:
        context['categories'] = categories
        context['category'] = category
        context['products'] = products
    return render(request, 'shop.html', context)


def search_by_price(request):
    context = {}
    categories = cache.get('categories')
    if not categories:
        context['categories'] = Category.objects.all()
        cache.set('categories', categories, 10)
    if request.method == 'POST':
        price = request.POST.get('price', '')
        if not price:
            context = {'empty_data': 'Nothing found', 'categories': categories}
            return render(request, 'shop.html', context=context)
        if int(price) >= 501:
            products = cache.get('products')
            if not products:
                context['products'] = Products.objects.filter(price__gte=price)
                cache.set('products', products, 10)
            else:
                context['products'] = products
            return render(request, 'shop.html', context=context)
        else:
            products = cache.get('products')
            if not products:
                context['products'] = Products.objects.filter(price__lte=price)
                cache.set('products', products, 10)
            else:
                context = {'products': products}
            return render(request, 'shop.html', context=context)
    else:
        context['categories'] = categories
    return render(request, 'shop.html')


def all_products(request):
    context = {}
    products = cache.get('products')
    categories = cache.get('categories')
    if not products or not categories:
        context['products'] = Products.objects.all()
        context['categories'] = Category.objects.all()
        cache.set('products', products, 10)
        cache.set('categories', categories, 10)
    else:
        context['categories'] = categories
        context['products'] = products
    return render(request, 'shop.html', context)


def contacts(request):
    return render(request, 'contacts.html')


def shop(request):
    context = {}
    categories = cache.get('categories')
    products = cache.get('products')
    if not categories or not products:
        context['categories'] = Category.objects.all()
        context['products'] = Products.objects.all()
        cache.set('categories', categories, 10)
        cache.set('products', products, 10)
    else:
        context['categories'] = categories
        context['products'] = products
    return render(request, 'shop.html', context)


def detail_product(request, product_id):
    product = Products.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'detail_product.html', context)


def search(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        print(search_query)
        if not search_query:
            context = {'empty_data': 'Nothing found', 'categories': categories}
        else:
            products = Products.objects.filter(
                Q(title__istartswith=str(search_query)[0].title())
                | Q(title__istartswith=str(search_query)[0].lower())
                | Q(title__icontains=search_query)
            )
            if not products.exists():
                context = {'empty_data': 'Nothing found', 'categories': categories}
            else:
                context = {'products': products, 'categories': categories}
        return render(request, 'shop.html', context=context)
    return render(request, 'shop.html')
