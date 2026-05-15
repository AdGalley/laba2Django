from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Application, Category
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

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


class ApplicationForm(forms.ModelForm):
    """Форма создания заявки"""

    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название заявки'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание заявки'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_photo(self):
        """Проверка файла изображения"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Проверка размера файла (2Мб = 2 * 1024 * 1024 байт)
            max_size = 2 * 1024 * 1024
            if photo.size > max_size:
                raise ValidationError('Размер файла не должен превышать 2Мб.')

            # Проверка формата файла
            valid_extensions = ['jpg', 'jpeg', 'png', 'bmp']
            file_extension = photo.name.split('.')[-1].lower()
            if file_extension not in valid_extensions:
                raise ValidationError('Допустимые форматы: jpg, jpeg, png, bmp.')

        return photo