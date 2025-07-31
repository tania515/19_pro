from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm, \
    PasswordChangeForm
from .models import CustomUser
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False)
    address = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'address', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class CustomUserLoginForm(AuthenticationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'autocomplete': 'username email',
            'class': 'form-control',
            'placeholder': 'Введите ваш email',
            'autofocus': True,
            'name': 'email',
            'id': 'email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль',
            'name': 'password',
            'id': 'password'
        })
    )

    field_order = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)  # Полностью удаляем поле username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email обязателен")

        # Проверяем, есть ли пользователь с таким email
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email не найден")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("Пароль обязателен")
        return password

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Пробуем аутентифицировать
            self.user_cache = authenticate(
                request=self.request,
                email=email,
                password=password
            )

            # Если аутентификация не удалась
            if not self.user_cache:
                # Проверяем существует ли пользователь
                user_exists = User.objects.filter(email=email).exists()

                if user_exists:
                    # Если существует, проверяем активность
                    user = User.objects.get(email=email)
                    if not user.is_active:
                        raise ValidationError("Аккаунт не активирован. Пожалуйста, проверьте вашу почту")
                    else:
                        raise ValidationError("Неверный пароль")
                else:
                    raise ValidationError("Пользователь с таким email не найден")

        return cleaned_data

    def get_user(self):
        return self.user_cache


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email',
            'autocomplete': 'email'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("Пользователь с таким email не найден или аккаунт не активирован")
        return email


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'address']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class AccountDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        label="Я подтверждаю удаление аккаунта",
        required=True
    )
