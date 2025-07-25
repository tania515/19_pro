from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomPasswordResetForm, CustomSetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import get_user_model

User = get_user_model()


def home(request):
    return render(request, 'shop/home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Аккаунт не активен до подтверждения email
            user.save()

            # Генерация токена для подтверждения email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirmation_link = request.build_absolute_uri(f'/activate/{uid}/{token}/')

            # Отправка email с подтверждением
            send_mail(
                'Подтверждение регистрации',
                f'Перейдите по ссылке для активации: {confirmation_link}',
                'admin@shop.com',
                [user.email]
            )
            return redirect('shop:home')
    #            return redirect('email_confirmation_sent')

    else:
        form = CustomUserCreationForm()

    return render(request, 'shop/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('shop:login')
    else:
        messages.error(request, "Ошибка активации.")
        return render(request, 'shop/home.html')


@login_required
def profile(request):
    return render(request, 'shop/profile.html')


def login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            try:
                # Пытаемся найти пользователя
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    auth_login(request, user)
                    messages.success(request, "Вы успешно авторизированы!")
                    return redirect('shop:profile')
                else:
                    messages.error(request, "Что то не так (email, пароль или нет активации")
            except CustomUser.DoesNotExist:
                # Обработка случая, когда пользователь не найден
                messages.error(request, "Пользователь не найден")
                return redirect('shop:login')

        else:
            messages.error(request, "Исправьте ошибки в форме.")

    else:
        form = CustomUserLoginForm(request)

    return render(request, 'shop/login.html', {'form': form})


def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)

            # Генерация токена для сброса пароля
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )

            send_mail(
                'Сброс пароля',
                f'Для сброса пароля перейдите по ссылке: {reset_link}',
                'admin@shop.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Письмо с инструкциями по сбросу пароля отправлено на ваш email')
            return redirect('shop:home')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'shop/password_reset.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        # Декодируем uid и получаем пользователя
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Проверяем токен
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ваш пароль успешно изменен!')
                return redirect('shop:login')
        else:
            form = CustomSetPasswordForm(user)

        return render(request, 'shop/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Ссылка для сброса пароля недействительна или устарела.')
        return redirect('shop:password_reset')