from django.urls import reverse
from django.shortcuts import render, redirect
from .models import CustomUser, Order
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomPasswordResetForm, \
    ProfileEditForm, CustomPasswordChangeForm, CustomSetPasswordForm, AccountDeleteForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import AccountDeletion

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


"""@login_required
def profile(request):
    return render(request, 'shop/profile.html')"""


@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(owner=user).order_by('-created_at')
    return render(request, 'shop/profile.html', {
        'user': user,
        'orders': orders
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('shop:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'shop/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен')
            return redirect('shop:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'shop/change_password.html', {'form': form})


@login_required
def account_delete_request(request):
    if request.method == 'POST':
        form = AccountDeleteForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm']:
            # Создаем запрос на удаление
            token = default_token_generator.make_token(request.user)
            AccountDeletion.objects.create(user=request.user, token=token)

            # Отправляем email
            uid = urlsafe_base64_encode(force_bytes(request.user.pk))
            delete_link = request.build_absolute_uri(
                reverse('shop:account_delete_confirm', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )
            send_mail(
                'Подтверждение удаления аккаунта',
                f'Для подтверждения удаления аккаунта перейдите по ссылке: {delete_link}',
                'noreply@yoursite.com',
                [request.user.email],
                fail_silently=False,
            )

            messages.info(request, 'Письмо с подтверждением отправлено на ваш email')
            return redirect('shop:profile')
    else:
        form = AccountDeleteForm()

    return render(request, 'shop/account_delete.html', {'form': form})


def account_delete_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
        deletion = AccountDeletion.objects.get(user=user, token=token)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist, AccountDeletion.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.delete()
        messages.success(request, 'Ваш аккаунт успешно удален')
        return redirect('shop:home')
    else:
        messages.error(request, 'Ссылка для удаления недействительна')
        return redirect('shop:profile')