from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from users.models import User

class Command(BaseCommand):
    help = 'Verifies user creation and authentication'

    def handle(self, *args, **kwargs):
        self.stdout.write('Verifying authentication...')

        # Define user credentials
        username = 'user1'
        email = 'user1@example.com'
        password = 'password'

        # Delete user if exists
        User.objects.filter(username=username).delete()

        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password)
        self.stdout.write(f'User "{username}" created.')
        self.stdout.write(f'Hashed password in DB: {user.password}')


        # Authenticate the user
        authenticated_user = authenticate(email=email, password=password)

        if authenticated_user is not None:
            self.stdout.write(self.style.SUCCESS(f'Successfully authenticated user "{username}".'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to authenticate user "{username}".'))

        # Clean up the created user
        user.delete()
        self.stdout.write(f'User "{username}" deleted.')
