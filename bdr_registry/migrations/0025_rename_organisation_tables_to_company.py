from south.v2 import SchemaMigration
from south.db import db


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('bdr_registry_organisation', 'bdr_registry_company')
        db.rename_table('bdr_registry_organisationnamehistory',
                        'bdr_registry_companynamehistory')

    def backwards(self, orm):
        db.rename_table('bdr_registry_company', 'bdr_registry_organisation')
        db.rename_table('bdr_registry_companynamehistory',
                        'bdr_registry_organisationnamehistory')
