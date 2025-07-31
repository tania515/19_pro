import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


def product_image_path(instance, filename):
    return os.path.join(
        'products',
        'updated_at',
        f'product_{instance.id}_{filename}'
    )


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание категория')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        verbose_name='Родительская категория',
        blank=True,
        null=True,
        related_name='children',
        help_text='Необязательное поле. Родительская категория.',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'db_category'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, null=False, verbose_name='Товар')
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        verbose_name='Цена товара'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    stock_quantity = models.PositiveIntegerField(default=1, verbose_name='Количество единиц на складе')
    image = models.ImageField(
        upload_to=product_image_path,
        null=True,
        verbose_name="Фото товара"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        unique_together = ['name', 'category']
        db_table = 'db_product'

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):

        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser,  PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=15, blank=True, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес доставки')
    is_active = models.BooleanField(default=False, verbose_name='Аккаунт активен')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=True,
        default=0.00,
        verbose_name='Итого'
    )
    status = models.CharField(
        choices=[("в обработке", "в обработке"), ("доставляется", "доставляется"), ("доставлено", "доставлено")],
        default="в обработке")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем заказ
        self._calculate_total()        # Затем пересчитываем сумму

    def _calculate_total(self):
        self.total = sum(item.item_price for item in self.items.all())
        super().save(update_fields=['total'])

    def __str__(self):
        return f"Заказ {self.owner.email} - {self.total} руб."

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        db_table = 'db_order'


class OrderItem(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_item = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_quantity = models.PositiveIntegerField(default=1)

    @property
    def item_price(self):
        return self.item.price * self.product_quantity

    def __str__(self):
        return f"{self.item.name} x {self.product_quantity} = {self.item_price}"

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        db_table = 'db_order_item'


class Feedback(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="feedbacks")
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    Rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Оценка от 1 до 5",
        default=5)
    feedback = models.TextField()

    def __str__(self):
        return f"{self.feedback} "

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        db_table = 'db_feedback'


class AccountDeletion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_deletions'
