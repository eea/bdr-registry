from django.core.management.base import BaseCommand

from bdr_registry.models import Company, Obligation, User
from bdr_registry.utils import set_role_for_account



class Command(BaseCommand):
    help = """
        Check the status of all HDV users and set the correct role for all accounts.
        Set the correct role for HDV_resim users as well.
    """

    def add_arguments(self, parser):
        parser.add_argument("-d", "--dry_run", type=bool, help="Dry run")

    def _handle_person(self, company, person, options):
        user = User.objects.filter(username=person.account.uid).first()
        if not user:
            print(f"User {person.account.uid} not found")
            return
        if user.is_active:
            if company.linked_hdv_company:
                print(f"Set ADD role for {person.account.uid} in {company.linked_hdv_company.name}")
                if not options["dry_run"]:
                    set_role_for_account(company.linked_hdv_company, person.account.uid, "add")
            print(f"Set ADD role for {person.account.uid} in {company.name}")
            if not options["dry_run"]:
                set_role_for_account(company, person.account.uid, "add")
        else:
            if company.linked_hdv_company:
                print(f"Set REMOVE role for {person.account.uid} in {company.linked_hdv_company.name}")
                if not options["dry_run"]:
                    set_role_for_account(company.linked_hdv_company, person.account.uid, "remove")
            print(f"Set REMOVE role for {person.account.uid} in {company.name}")
            if not options["dry_run"]:
                set_role_for_account(person.company, person.account.uid, "remove")

    def handle(self, *args, **options):
        if options["dry_run"]:
            print("Dry run")
        hdv_obligation = Obligation.objects.get(code="hdv")
        companies = Company.objects.filter(obligation=hdv_obligation)
        for company in companies:
            for person in company.people.all():
                if person.account:
                    self._handle_person(company, person, options)
