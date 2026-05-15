from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-application/', views.create_application, name='create_application'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('delete-application/<int:pk>/', views.delete_application, name='delete_application'),

    # Маршруты для администратора
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('change-status-in-progress/<int:pk>/', views.change_status_to_in_progress, name='change_status_in_progress'),
    path('change-status-completed/<int:pk>/', views.change_status_to_completed, name='change_status_completed'),
    path('category-list/', views.category_list, name='category_list'),
    path('category-create/', views.category_create, name='category_create'),
    path('category-delete/<int:pk>/', views.category_delete, name='category_delete'),
]