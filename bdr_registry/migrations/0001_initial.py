# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table('bdr_registry_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('bdr_registry', ['Country'])

        # Adding model 'Organisation'
        db.create_table('bdr_registry_organisation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('addr_street', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('addr_place1', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('addr_postalcode', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('addr_place2', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bdr_registry.Country'])),
        ))
        db.send_create_signal('bdr_registry', ['Organisation'])

        # Adding model 'Person'
        db.create_table('bdr_registry_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('family_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='people', to=orm['bdr_registry.Organisation'])),
        ))
        db.send_create_signal('bdr_registry', ['Person'])


    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table('bdr_registry_country')

        # Deleting model 'Organisation'
        db.delete_table('bdr_registry_organisation')

        # Deleting model 'Person'
        db.delete_table('bdr_registry_person')


    models = {
        'bdr_registry.country': {
            'Meta': {'object_name': 'Country'},
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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