from django.core.management.base import BaseCommand

from bdr_registry.ldap_editor import create_ldap_editor
from bdr_registry.models import Account


class Command(BaseCommand):
    help = "Check if ldap accounts are created. If they are not, they will be created."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", type=bool, default=True)

    def handle(self, *args, **options):
        accounts = Account.objects.all()
        ldap_editor = create_ldap_editor()
        for account in accounts:
            result = ldap_editor.search_account(account.uid)
            if not result:
                self.stdout.write(
                    "Account {uid} does not exist in LDAP.".format(uid=account.uid)
                )
                if options["dry_run"]:
                    continue

                ldap_editor.create_account(
                    account.uid,
                    account.company.name,
                    account.company.country.name,
                    account.password,
                )
                self.stdout.write("Account {uid} created.".format(uid=account.uid))
