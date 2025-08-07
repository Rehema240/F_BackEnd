import random
from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database...')

        # Clear existing data
        User.objects.all().delete()

        # Create dummy users
        for i in range(10):
            User.objects.create(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password',
                phone_number=f'123456789{i}',
                role=random.choice(['student', 'employee','admin','head'])
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))
