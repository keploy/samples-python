from django.urls import path
from .views import ItemViewSet

urlpatterns = [
    path('items/', ItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('items/<str:pk>/', ItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]