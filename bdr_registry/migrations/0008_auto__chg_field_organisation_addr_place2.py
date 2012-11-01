# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Organisation.addr_place2'
        db.alter_column('bdr_registry_organisation', 'addr_place2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # Changing field 'Organisation.addr_place2'
        db.alter_column('bdr_registry_organisation', 'addr_place2', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    models = {
        'bdr_registry.account': {
            'Meta': {'object_name': 'Account'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'bdr_registry.apikey': {
            'Meta': {'object_name': 'ApiKey'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'8bjib33ahphl67w7fv8u'", 'max_length': '255'})
        },
        'bdr_registry.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'bdr_registry.obligation': {
            'Meta': {'object_name': 'Obligation'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'bdr_registry.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bdr_registry.Account']", 'null': 'True', 'blank': 'True'}),
            'addr_place1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'addr_place2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'addr_postalcode': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'addr_street': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bdr_registry.Country']"}),
            'date_registered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'obligation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bdr_registry.Obligation']", 'null': 'True', 'blank': 'True'})
        },
        'bdr_registry.person': {
            'Meta': {'object_name': 'Person'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'people'", 'to': "orm['bdr_registry.Organisation']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['bdr_registry']