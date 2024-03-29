from bdr_registry.models import Company, Country, Obligation
from bdr_registry.utils import create_reporting_folder, set_role_for_account

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clone HDV companies into HDV resim"

    def handle(self, *args, **options):
        hdv_obligation = Obligation.objects.get(code="hdv")
        hdv_resim_obligation = Obligation.objects.get(code="hdv_resim")
        eu_country = Country.objects.get(code="eu")
        companies = Company.objects.filter(obligation=hdv_obligation)
        for company in companies:
            old_company = Company.objects.get(id=company.id)
            company.pk = None
            company.obligation = hdv_resim_obligation
            company.linked_hdv_company = old_company
            company.country = eu_country
            company._state.adding = True
            company.save()
            if company.account:
                create_reporting_folder(company)
            for person in old_company.people.all():
                person.pk = None
                person.company = company
                person._state.adding = True
                person.save()
                if person.account and company.account:
                    set_role_for_account(person.company, person.account.uid, "add")
