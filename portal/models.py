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
    # Логин латиница
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[latin_validator],
        help_text='Только латинские буквы и дефис.'
    )

    # Фамилия кириллица
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        validators=[cyrillic_validator],
        help_text='Только кириллица.'
    )

    # Имя кириллица
    first_name = models.CharField(
        'Имя',
        max_length=150,
        validators=[cyrillic_validator],
        help_text='Только кириллица.'
    )

    # Отчество кириллица
    middle_name = models.CharField(
        'Отчество',
        max_length=150,
        validators=[cyrillic_validator],
        blank=True,  # Можно оставить пустым
        help_text='Только кириллица.'
    )

    # поле для входа
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name or ""}'.strip()


class Category(models.Model):
    """Категория заявки"""
    name = models.CharField(
        'Название категории',
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Application(models.Model):
    """Заявка на разработку дизайна"""

    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    )

    title = models.CharField(
        'Название',
        max_length=200
    )
    description = models.TextField(
        'Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='applications'
    )
    photo = models.ImageField(
        'Фото помещения',
        upload_to='applications/%Y/%m/%d/',
        blank=True,
        null=True
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='applications'
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']  # Сортировка по убыванию даты

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def can_delete(self):
        """Проверка возможности удаления заявки"""
        return self.status == 'new'