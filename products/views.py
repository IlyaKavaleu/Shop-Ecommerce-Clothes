from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from .models import Products, Category


def index(request):
    return render(request, 'index.html')


def detail_category(request, category_id):
    categories = Category.objects.all()
    category = Category.objects.get(id=category_id)
    products = Products.objects.filter(category=category)
    context = {'category': category, 'products': products, 'categories': categories}
    return render(request, 'shop.html', context)


def search_by_price(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        price = request.POST.get('price', '')
        if not price:
            context = {'empty_data': 'Nothing found', 'categories': categories}
            return render(request, 'shop.html', context=context)
        if int(price) >= 501:
            products = Products.objects.filter(price__gte=price)
            context = {'products': products, 'categories': categories}
            return render(request, 'shop.html', context=context)
        else:
            products = Products.objects.filter(price__lte=price)
            context = {'products': products, 'categories': categories}
            return render(request, 'shop.html', context=context)
    return render(request, 'shop.html')


def all_products(request):
    products = Products.objects.all()
    categories = Category.objects.all()
    context = {'products': products, 'categories': categories}
    return render(request, 'shop.html', context)


def contacts(request):
    return render(request, 'contacts.html')


def shop(request):
    categories = Category.objects.all()
    products = Products.objects.all()
    context = {'categories': categories, 'products': products}
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
