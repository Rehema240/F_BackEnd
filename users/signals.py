from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Opportunity
from notification.models import Notification

@receiver(post_save, sender=Opportunity)
def create_opportunity_notification(sender, instance, created, **kwargs):
    if created:
        students = User.objects.filter(role='student')
        for student in students:
            Notification.objects.create(
                recipient=student,
                sender=instance.employee,
                message=f"New opportunity posted: {instance.title}"
            )
