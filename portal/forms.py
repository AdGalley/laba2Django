from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import CustomUser
from django.core.validators import RegexValidator

# Валидаторы
cyrillic_validator = RegexValidator(
    regex=r'^[а-яА-ЯёЁ\s\-]+$',
    message='Допустимы только кириллические буквы, пробелы и дефис.'
)

latin_validator = RegexValidator(
    regex=r'^[a-zA-Z\-]+$',
    message='Допустимы только латинские буквы и дефис.'
)


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""

    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        validators=[cyrillic_validator]
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        validators=[cyrillic_validator]
    )
    middle_name = forms.CharField(
        label='Отчество',
        max_length=150,
        required=False,
        validators=[cyrillic_validator]
    )
    username = forms.CharField(
        label='Логин',
        max_length=150,
        validators=[latin_validator],
        help_text='Только латинские буквы и дефис.'
    )
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
    agreement = forms.BooleanField(label='Согласие на обработку персональных данных')

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'middle_name', 'username', 'email', 'password1', 'password2', 'agreement']

    def clean_agreement(self):
        agreement = self.cleaned_data.get('agreement')
        if not agreement:
            raise forms.ValidationError('Необходимо дать согласие на обработку персональных данных.')
        return agreement

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Этот логин уже занят.')
        return username


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа пользователя"""
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput,
    )