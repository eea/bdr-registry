from django.core.management.base import BaseCommand
from bdr_registry.models import Company, Country, Obligation
import json
import requests


class Command(BaseCommand):
    help = "Creates companies from a request provided.updated_since looks like DD/MM/YYYY"

    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('--updated_since', type=str, default='10/10/2017')

    def handle(self, *args, **options):
        headers = {
            'user': options['user'],
            'password': options['password']
        }
        updated_since = options['updated_since']
        url = 'https://webgate.acceptance.ec.europa.eu/ods2/rest/api/latest/odsundertakings?updatedSince=' + updated_since
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            self.stdout.write("Bad response.")
            return;
        companies = json.loads(resp.content)
        for company in companies:
            country = Country.objects.filter(
                code=company['address']['country']['code'].lower()).first()
            obligation = Obligation.objects.filter(code=company['domain'].lower()).first()
            Company.objects.all().update_or_create(
                vat_number=company['eoriNumber'], defaults={
                'name': company['name'],
                'addr_street': company['address']['street'],
                'addr_place1': company['address']['city'],
                'addr_postalcode': company['address']['zipCode'],
                'addr_place2': company['address']['country']['type'],
                'vat_number': company['eoriNumber'],
                'country_id': country.id,
                'obligation_id': obligation.id,
                'website': company['website']
            })
            self.stdout.write("Company {name} created.".format(
                name=company['name']
            ))
