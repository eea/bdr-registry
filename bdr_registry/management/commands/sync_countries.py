from django.conf import settings
import requests
import json

from django.core.management.base import BaseCommand, CommandError

from bdr_registry.models import Country


class Command(BaseCommand):

    help = "Gets a country list from %s and adds to the application's DB the " \
           "ones that are not already present." % settings.LOCALITIES_TABLE_URL

    def handle(self, *args, **options):
        url = settings.LOCALITIES_TABLE_URL
        r = requests.get(url)

        if r.status_code != 200:
            raise CommandError('GET {0} returned {1}'.format(url,
                                                             r.status_code))

        countries = json.loads(r.text.replace("'", '"'))

        countries_added = 0
        for country_dict in countries:
            try:
                country, created = Country.objects.get_or_create(
                    name=country_dict['name'],
                    code=country_dict['iso'].lower()
                )
                if created:
                    self.stdout.write('Added new country: %s' % country)
                    countries_added += 1

            except Exception as e:
                self.stderr.write('DB exception: %s' % e)

        if not countries_added:
            self.stdout.write('No new countries added.')
