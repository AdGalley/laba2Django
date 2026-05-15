from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def index(request):
    """Главная страница"""
    return render(request, 'portal/index.html')

def register_view(request):
    """Представление регистрации"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'portal/register.html', {'form': form})

def login_view(request):
    """Представление входа"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            # Выводим ошибки для отладки
            print("Ошибки формы:", form.errors)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})

def logout_view(request):
    """Представление выхода"""
    logout(request)
    return redirect('home')