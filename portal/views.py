from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, ApplicationForm,
    ChangeStatusToCompletedForm, ChangeStatusToInProgressForm, CategoryForm
)
from .models import Application, Category


def is_admin(user):
    """Проверка, является ли пользователь администратором"""
    return user.is_authenticated and user.is_staff


def index(request):
    """Главная страница"""
    # Получаем не более 4 последних выполненных заявок
    completed_applications = Application.objects.filter(
        status='completed'
    ).order_by('-created_at')[:4]

    # Считаем количество заявок в статусе "Принято в работу"
    in_progress_count = Application.objects.filter(
        status='in_progress'
    ).count()

    context = {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    }

    return render(request, 'portal/index.html', context)


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
            application.status = 'new'
            application.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'portal/create_application.html', {'form': form})


@login_required
def my_applications(request):
    """Просмотр своих заявок"""
    applications = Application.objects.filter(user=request.user).order_by('-created_at')

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

    if application.status != 'new':
        messages.error(request, 'Нельзя удалить заявку, которая находится в работе или выполнена.')
        return redirect('my_applications')

    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Заявка успешно удалена!')
        return redirect('my_applications')

    return render(request, 'portal/delete_application.html', {'application': application})


# ==========================================
# ФУНКЦИИ АДМИНИСТРАТОРА (ПР 2.3)
# ==========================================

@login_required
@user_passes_test(is_admin, login_url='home')
def admin_dashboard(request):
    """Панель управления администратора - список всех заявок"""
    applications = Application.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications,
        'status_filter': status_filter,
    }
    return render(request, 'portal/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='home')
def change_status_to_in_progress(request, pk):
    """Смена статуса на 'Принято в работу'"""
    application = get_object_or_404(Application, pk=pk)

    if application.status != 'new':
        messages.error(request, 'Нельзя изменить статус заявки, которая уже в работе или выполнена.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = ChangeStatusToInProgressForm(request.POST, instance=application)
        if form.is_valid():
            application.status = 'in_progress'
            application.updated_at = timezone.now()
            form.save()
            messages.success(request, f'Заявка "{application.title}" принята в работу.')
            return redirect('admin_dashboard')
    else:
        form = ChangeStatusToInProgressForm(instance=application)

    return render(request, 'portal/change_status_in_progress.html', {
        'form': form,
        'application': application
    })


@login_required
@user_passes_test(is_admin, login_url='home')
def change_status_to_completed(request, pk):
    """Смена статуса на 'Выполнено'"""
    application = get_object_or_404(Application, pk=pk)

    if application.status != 'new':
        messages.error(request, 'Нельзя изменить статус заявки, которая уже в работе или выполнена.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = ChangeStatusToCompletedForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            application.status = 'completed'
            application.updated_at = timezone.now()
            form.save()
            messages.success(request, f'Заявка "{application.title}" выполнена.')
            return redirect('admin_dashboard')
    else:
        form = ChangeStatusToCompletedForm(instance=application)

    return render(request, 'portal/change_status_completed.html', {
        'form': form,
        'application': application
    })


@login_required
@user_passes_test(is_admin, login_url='home')
def category_list(request):
    """Список категорий"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'portal/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin, login_url='home')
def category_create(request):
    """Создание категории"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно создана.')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'portal/category_form.html', {'form': form, 'action': 'create'})


@login_required
@user_passes_test(is_admin, login_url='home')
def category_delete(request, pk):
    """Удаление категории"""
    category = get_object_or_404(Category, pk=pk)
    applications_count = category.applications.count()

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория "{category_name}" и все её заявки ({applications_count}) удалены.')
        return redirect('category_list')

    return render(request, 'portal/category_delete.html', {
        'category': category,
        'applications_count': applications_count
    })