from django.urls import path
from .views import (
    eventListCreateView,
    eventRetrieveUpdateDestroyView,
    eventApplicationConfirmView,
)

urlpatterns = [
    path('events/', eventListCreateView, name='event-list-create'),
    path('events/<int:pk>/', eventRetrieveUpdateDestroyView, name='event-detail'),
    path('applications/<int:pk>/confirm/', eventApplicationConfirmView, name='event-application-confirm'),
]
