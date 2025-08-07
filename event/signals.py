from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from notification.models import Notification
from .models import Event

@receiver(post_save, sender=Event)
def create_event_notification(sender, instance, created, **kwargs):
    if created:
        students = User.objects.filter(role='student')
        for student in students:
            Notification.objects.create(
                recipient=student,
                sender=instance.employee,
                message=f"New event posted: {instance.title}"
            )
