
from django.contrib.sessions.backends.db import SessionStore
from .models import Cart, CartItem
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AnonymousUser


def get_or_create_cart(request):
    # Создаем сессию, если ее нет
    if not request.session.session_key:
        request.session.create()

    # Получаем или создаем объект сессии
    session, _ = Session.objects.get_or_create(session_key=request.session.session_key)

    if request.user.is_authenticated:
        # Для авторизованных пользователей
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Если есть сессионная корзина - объединяем
        session_cart = Cart.objects.filter(session=session).exclude(pk=cart.pk).first()
        if session_cart:
            cart.merge_with_session(session_cart)
    else:
        # Для гостей
        cart, created = Cart.objects.get_or_create(session=session)

    return cart


def merge_carts(source_cart, target_cart):
    for item in source_cart.items.all():
        # Пытаемся найти такой же товар в целевой корзине
        try:
            target_item = target_cart.items.get(product=item.product)
            target_item.quantity += item.quantity
            target_item.save()
        except CartItem.DoesNotExist:
            # Если нет такого товара, просто переносим
            item.cart = target_cart
            item.save()
    # Удаляем исходную корзину
    source_cart.delete()