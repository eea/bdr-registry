# -*- coding: utf-8 -*-

import csv
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from bdr_registry.models import Company


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--file',
            dest='filename',
            help='Import and update the companies EORI value from a TSV file'),
        )

    def handle(self, *args, **options):

        if options['filename']:
            try:
                with open(options['filename'], 'rb') as f:
                    reader = csv.reader(f, delimiter='\t')
                    reader.next()

                    for row in reader:
                        if row[2] and row[8]:  #account_id and eori
                            try:
                                org = Company.objects.get(id=row[0])
                                org.eori = row[8]
                                org.save()
                                self.stdout.write('Update '
                                    'organisation: %s\n' % org.id)
                            except Company.DoesNotExist:
                                pass

                self.stdout.write('Update successful.\n')
            except IOError:
                raise CommandError('File not found')
        else:
            raise CommandError('Missing argument --file')
