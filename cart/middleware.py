from django.utils.deprecation import MiddlewareMixin
from .utils import get_or_create_cart


class CartMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.cart = get_or_create_cart(request)


class CartSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Убедимся, что сессия существует
        if not request.session.session_key:
            request.session.create()

        response = self.get_response(request)

        # Сохраняем сессию, если в корзине есть товары
        if hasattr(request, 'cart') and request.cart.items.exists():
            request.session.modified = True

        return response
