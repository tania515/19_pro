from django.db import models
from django.contrib.sessions.models import Session
from shop.models import Product, CustomUser


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=True,
        default=0.00,
        verbose_name='Итого'
    )

    class Meta:
        unique_together = [['user', 'session']]
        ordering = ['session']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        db_table = 'db_cart'

    def _calculate_total(self):
        self.total = sum(item.item_price for item in self.items.all())
        super().save(update_fields=['total'])

    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.email} - {self.total} руб."
        return f"Сессионная корзина {self.session.session_key}"

    def merge_with_session(self, session_cart):
        """Переносит товары из сессионной корзины"""
        for item in session_cart.items.all():
            existing_item = self.items.filter(item=item.item).first()
            if existing_item:
                existing_item.product_quantity += item.product_quantity
                existing_item.save()
            else:
                item.cart_item = self
                item.save()
        session_cart.delete()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем
        self._calculate_total()        # Затем пересчитываем сумму


class CartItem(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_item = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def item_price(self):
        return self.item.price * self.product_quantity

    def __str__(self):
        return f"{self.item.name} x {self.product_quantity} = {self.item_price}"

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        db_table = 'db_cart_item'


