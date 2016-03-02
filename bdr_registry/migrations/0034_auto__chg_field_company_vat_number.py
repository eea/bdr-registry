# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Company.vat_number'
        db.alter_column(u'bdr_registry_company', 'vat_number', self.gf('django.db.models.fields.CharField')(default='MISSING', max_length=17))

    def backwards(self, orm):

        # Changing field 'Company.vat_number'
        db.alter_column(u'bdr_registry_company', 'vat_number', self.gf('django.db.models.fields.CharField')(max_length=17, null=True))

    complete_apps = ['bdr_registry']
