from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates an owner user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='owner', help='Username for owner')
        parser.add_argument('--email', type=str, default='owner@midya.com', help='Email for owner')
        parser.add_argument('--password', type=str, default='owner123', help='Password for owner')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists.'))
            return
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='owner'
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created owner user "{username}"'))

