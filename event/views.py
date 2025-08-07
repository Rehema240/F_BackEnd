from django.shortcuts import render
from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema
from .models import Event, EventApplication
from .serializers import EventSerializer, EventApplicationSerializer

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class EventRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]


eventListCreateView = swagger_auto_schema(
    method='post',
    responses={201: EventSerializer()}
)(EventListCreateView.as_view())
eventRetrieveUpdateDestroyView = swagger_auto_schema(
    method='get',
    responses={200: EventSerializer()}
)(EventRetrieveUpdateDestroyView.as_view())


class EventApplicationConfirmView(generics.RetrieveUpdateAPIView):
    queryset = EventApplication.objects.all()
    serializer_class = EventApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return EventApplication.objects.none()
        return EventApplication.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to update this application.")
        
        if serializer.validated_data.get('status') == 'accepted':
            serializer.save(status='accepted')
        else:
            serializer.save()

eventApplicationConfirmView = swagger_auto_schema(
    method='patch',
    request_body=EventApplicationSerializer,
    responses={200: EventApplicationSerializer()}
)(EventApplicationConfirmView.as_view())
