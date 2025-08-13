from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from shop.models import Product
from .models import CartItem, Cart
from .utils import get_or_create_cart
from django.contrib import messages


def add_to_cart(request, product_id=None):
    if request.method == 'POST' and not product_id:
        product_id = request.POST.get('product_id')

    item = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart_item=cart,
        item=item,
        defaults={'product_quantity': quantity}
    )

    if not created:
        cart_item.product_quantity += quantity
        cart_item.save()

    cart._calculate_total()  # Обновляем общую сумму корзины
    messages.success(request, f"Товар {item.name} добавлен в корзину")
    return redirect(reverse('shop:profile'))  # Перенаправляем обратно в профиль


def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart_item=cart)

    if request.method == 'POST':
        item.delete()
        cart._calculate_total()
        messages.success(request, "Товар удален из корзины")
        return redirect(reverse('shop:profile'))

    return render(request, 'cart/remove.html', {'item': item})


def update_quantity(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart_item=cart)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.product_quantity = quantity
            item.save()
            cart._calculate_total()
            messages.success(request, "Количество товара обновлено")
        else:
            item.delete()
            messages.success(request, "Товар удален из корзины")
        return redirect(reverse('shop:profile'))

    return render(request, 'cart/update_quantity.html', {'item': item})


def view_cart(request):
    try:
        cart = get_or_create_cart(request)
        # Используйте правильное имя поля для связи с элементами корзины
        cart_items = cart.items.all()  # или другое правильное имя related_name
        available_products = Product.objects.all()
        if request.user.is_authenticated:
            return render(request, 'shop/profile.html', {
                'cart': cart,
                'items': cart_items,  # Передаем элементы корзины отдельно
                'available_products': available_products
            })
        else:
            return render(request, 'cart/view.html', {
                'cart': cart,
                'items': cart_items,  # Передаем элементы корзины отдельно
                'available_products': available_products
            })
    except Exception as e:
        print(f"Error: {e}")  # Для отладки
        raise

