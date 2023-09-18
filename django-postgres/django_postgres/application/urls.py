from django.urls import path
from . import views


urlpatterns = [
    path('<uuid>/', views.get_update_deleteUser, name="get_update_deleteUser"), # get, put, delete
    path('', views.getAll_createUser, name='getAll_createUser') # get all, post
]