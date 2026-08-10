from django.urls import path
from . import views

urlpatterns = [
    path('employee/', views.get_all_employees),
    path('employee/<int:pk>/', views.get_employee),
    path('employee/create/', views.create_employee),
    path('employee/update/<int:pk>/', views.update_employee),
    path('employee/delete/<int:pk>/', views.delete_employee),
]