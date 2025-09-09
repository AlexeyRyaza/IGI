from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile
from datetime import date

class Command(BaseCommand):
    help = 'Creates user profiles for existing users that don\'t have one'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)
        for user in users_without_profile:
            Profile.objects.create(
                user=user,
                birth_date=date.today()  # временная дата для существующих пользователей
            )
            self.stdout.write(self.style.SUCCESS(f'Created profile for user {user.username}')) 