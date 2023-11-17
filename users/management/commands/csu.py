from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='doctor_linchenko@mail.ru',
            first_name='Andrey',
            last_name='Linchenko',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        user.set_password('02011999')
        user.save()

