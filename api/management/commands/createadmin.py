from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from app_pay.settings import env


class Command(BaseCommand):

    def handle(self, *args, **options):
        User = get_user_model()
        User.objects.create_superuser(env('SUPERUSER_NAME'), env('SUPERUSER_EMAIL'), env('SUPERUSER_PASSWORD'))
