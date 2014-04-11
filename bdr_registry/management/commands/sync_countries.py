from django.conf import settings
from django.db import IntegrityError
import requests
import json

from django.core.management.base import BaseCommand, CommandError

from bdr_registry.models import Country


class Command(BaseCommand):

    help = "Gets a country list from %s and adds the ones that are not " \
           "already present in the DB" % settings.LOCALITIES_TABLE_URL

    def handle(self, *args, **options):
        url = settings.LOCALITIES_TABLE_URL
        r = requests.get(url)

        if r.status_code != 200:
            raise CommandError('GET {0} returned {1}'.format(url,
                                                             r.status_code))

        countries_dict = json.loads(r.text.replace("'", '"'))
        countries = map(lambda c: Country(name=c['name'],
                                          code=c['iso'].lower()),
                        countries_dict)

        countries_added = 0
        for country in countries:
            try:
                country.save()
                self.stdout.write('Added %s' % country)
                countries_added += 1
            except IntegrityError:
                pass
            except Exception as e:
                self.stderr.write('Unexpected exception: %s' % e)

        if not countries_added:
            self.stdout.write('No new countries added')
