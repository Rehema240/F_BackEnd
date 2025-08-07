from rest_framework import serializers
from .models import Event, EventApplication

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'employee', 'title', 'description', 'duration', 'deadline', 'created_at', 'number_of_participant']
        read_only_fields = ['id', 'created_at']

class EventApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventApplication
        fields = ['id', 'event', 'user', 'status', 'applied_at']
        read_only_fields = ['id', 'user', 'applied_at']
