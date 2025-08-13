from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from .models import Cart
from cart.utils import merge_carts


@receiver(user_logged_in)
def merge_session_cart(sender, request, user, **kwargs):
    # Если есть сессионная корзина
    if 'session_cart_id' in request.session:
        try:
            session_cart = Cart.objects.get(id=request.session['session_cart_id'], user=None)
            user_cart, created = Cart.objects.get_or_create(user=user)
            merge_carts(session_cart, user_cart)
            del request.session['session_cart_id']
        except Cart.DoesNotExist:
            pass