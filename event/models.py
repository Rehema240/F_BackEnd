from django.db import models

# Create your models here.

class Event(models.Model):
    employee = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    # photos = models.ImageField(upload_to='event_photos/', blank=True, null=True)
    description = models.TextField()
    duration = models.DurationField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    number_of_participant = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class EventApplication(models.Model):
    STATUS_CHOICES = [
        ('on_progress', 'On progress'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='event_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='on_progress')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} - {self.status}"
