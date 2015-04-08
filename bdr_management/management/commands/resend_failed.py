from post_office.models import Email, STATUS
from post_office.mail import _send_bulk
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Resend mails that failed initially to send. Update db after."

    def handle(self, *args, **options):
        failed_emails = Email.objects.filter(status=STATUS.failed)
        (sent_count, failed_count) = _send_bulk(failed_emails)
        self.stdout.write(
            "Sent: {}. Failed: {}".format(sent_count, failed_count))
