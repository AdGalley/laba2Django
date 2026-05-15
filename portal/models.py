from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

# Валидатор для кириллицы (ФИО)
cyrillic_validator = RegexValidator(
    regex=r'^[а-яА-ЯёЁ\s\-]+$',
    message='Допустимы только кириллические буквы, пробелы и дефис.'
)

# Валидатор для латиницы (Логин)
latin_validator = RegexValidator(
    regex=r'^[a-zA-Z\-]+$',
    message='Допустимы только латинские буквы и дефис.'
)


class CustomUser(AbstractUser):
    # Логин (username) - только латиница
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[latin_validator],
        help_text='Только латинские буквы и дефис.'
    )

    # Фамилия - кириллица
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        validators=[cyrillic_validator],
        help_text='Только кириллица.'
    )

    # Имя - кириллица
    first_name = models.CharField(
        'Имя',
        max_length=150,
        validators=[cyrillic_validator],
        help_text='Только кириллица.'
    )

    # Отчество - кириллица (необязательное)
    middle_name = models.CharField(
        'Отчество',
        max_length=150,
        validators=[cyrillic_validator],
        blank=True,  # Можно оставить пустым
        help_text='Только кириллица.'
    )

    # Указываем поле для входа
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name or ""}'.strip()