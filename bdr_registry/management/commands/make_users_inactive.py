from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    args = "<prefix>"
    help = "Sets all users with FGAS usernames as inactive"

    def handle(self, *args, **options):
        if len(args) == 0:
            self.stderr.write(
                "Please specify a prefix. Usage: ./manage.py make_users_inactive"
            )
            return

        users = User.objects.filter(
            username__startswith=args[0], is_active=True
        ).update(is_active=False)
        self.stdout.write("{0} records updated.".format(users))
