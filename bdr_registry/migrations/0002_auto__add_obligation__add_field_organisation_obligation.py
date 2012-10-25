# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Obligation'
        db.create_table('bdr_registry_obligation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('bdr_registry', ['Obligation'])

        # Adding field 'Organisation.obligation'
        db.add_column('bdr_registry_organisation', 'obligation',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bdr_registry.Obligation'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Obligation'
        db.delete_table('bdr_registry_obligation')

        # Deleting field 'Organisation.obligation'
        db.delete_column('bdr_registry_organisation', 'obligation_id')


    models = {
        'bdr_registry.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'bdr_registry.obligation': {
            'Meta': {'object_name': 'Obligation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'bdr_registry.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'addr_place1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'addr_place2': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'addr_postalcode': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'addr_street': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bdr_registry.Country']"}),
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