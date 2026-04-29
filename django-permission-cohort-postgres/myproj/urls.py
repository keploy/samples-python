from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health),
    path("lookup/<str:app_label>/<str:model>/", views.lookup),
]
