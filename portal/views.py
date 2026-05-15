from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ApplicationForm
from .models import Application


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
        form = CustomAuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})


def logout_view(request):
    """Представление выхода"""
    logout(request)
    return redirect('home')


@login_required
def create_application(request):
    """Создание новой заявки"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'new'  # Автоматически устанавливаем статус "Новая"
            application.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'portal/create_application.html', {'form': form})


@login_required
def my_applications(request):
    """Просмотр своих заявок"""
    # Получаем все заявки текущего пользователя
    applications = Application.objects.filter(user=request.user).order_by('-created_at')

    # Фильтрация по статусу (если передан параметр)
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications,
        'status_filter': status_filter,
    }
    return render(request, 'portal/my_applications.html', context)


@login_required
def delete_application(request, pk):
    """Удаление заявки"""
    application = get_object_or_404(Application, pk=pk, user=request.user)

    # Проверяем, можно ли удалить заявку (только со статусом "Новая")
    if application.status != 'new':
        messages.error(request, 'Нельзя удалить заявку, которая находится в работе или выполнена.')
        return redirect('my_applications')

    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Заявка успешно удалена!')
        return redirect('my_applications')

    return render(request, 'portal/delete_application.html', {'application': application})