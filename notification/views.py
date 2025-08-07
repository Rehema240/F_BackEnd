from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer
from drf_yasg.utils import swagger_auto_schema

class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class NotificationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user)

notificationListCreateView = swagger_auto_schema(
    method='post',
    responses={201: NotificationSerializer()}
)(NotificationListCreateView.as_view())
notificationRetrieveUpdateDestroyView = swagger_auto_schema(
    method='get',
    responses={200: NotificationSerializer()}
)(NotificationRetrieveUpdateDestroyView.as_view())
