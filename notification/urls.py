from django.urls import path
from .views import (
    notificationListCreateView,
    notificationRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('notifications/', notificationListCreateView, name='notification-list-create'),
    path('notifications/<int:pk>/', notificationRetrieveUpdateDestroyView, name='notification-detail'),
]
