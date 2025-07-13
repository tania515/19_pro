from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate


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
        #return render(request, 'activation_invalid.html')
        return render(request, 'shop/home.html')


@login_required
def profile(request):
    return render(request, 'shop/profile.html')


def login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)  # Добавляем request
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Аутентификация пользователя
            user = authenticate(request, email=email, password=password)

            if user is not None:
                auth_login(request, user)  # Используем auth_login для ясности
                messages.success(request, "Вы успешно авторизированы!")
                return redirect('shop:profile')
            else:
                messages.error(request, "Ошибка аутентификации")
        else:
            messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = CustomUserLoginForm(request)  # Передаем request

    return render(request, 'shop/login.html', {'form': form})