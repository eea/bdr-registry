from bdr_registry.models import Company, Obligation
from bdr_registry.utils import set_role_for_account
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
        Delete HDV resim companies and persons and remove access to folder for their
        accounts and company account. The company folder is not removed #todo check if it can be removed
    """

    def handle(self, *args, **options):
        hdv_resim_obligation = Obligation.objects.get(code='hdv_resim')
        companies = Company.objects.filter(obligation=hdv_resim_obligation)
        for company in companies:  
            for person in company.people.all():
                if person.account:
                    set_role_for_account(person.company, person.account.uid, "remove")
                person.delete()
            if company.account:
                set_role_for_account(company, company.account.uid, "remove")
            company.delete()
            