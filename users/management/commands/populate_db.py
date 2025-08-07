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
            role_choice = random.choice(['student', 'employee','admin','head'])
            is_staff = True if role_choice == 'admin' else False
            is_superuser = True if role_choice == 'admin' else False

            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password',
                phone_number=f'123456789{i}',
                role=role_choice,
                is_staff=is_staff,
                is_superuser=is_superuser
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))
