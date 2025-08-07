from django.urls import path
from .views import (
    userListCreateView, userRetrieveUpdateDestroyView,
    loginAPIView,
    OpportunityListCreateView, OpportunityDetailView,
    userProfileView,
    changePasswordView,
    adminStatisticsAPIView # Added this line
)

urlpatterns = [
    path('users/', userListCreateView, name='user-list-create'),
    path('users/<int:pk>/', userRetrieveUpdateDestroyView, name='user-detail'),
    path('login/', loginAPIView, name='login'),
    path('me/', userProfileView, name='user-profile'),
    path('change-password/', changePasswordView, name='change-password'),
    path('opportunities/', OpportunityListCreateView.as_view(), name='opportunity-list-create'),
    path('opportunities/<int:pk>/', OpportunityDetailView.as_view(), name='opportunity-detail'),
    path('admin/statistics/', adminStatisticsAPIView, name='admin-statistics'),
]
