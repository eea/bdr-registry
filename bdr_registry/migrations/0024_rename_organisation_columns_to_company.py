from south.v2 import SchemaMigration
from south.db import db


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('bdr_registry_organisationnamehistory',
                         'organisation_id', 'company_id')
        db.rename_column('bdr_registry_comment', 'organisation_id', 'company_id')
        db.rename_column('bdr_registry_person', 'organisation_id', 'company_id')

    def backwards(self, orm):
        db.rename_column('bdr_registry_companynamehistory',
                         'company', 'organisation')
        db.rename_column('bdr_registry_comment',
                         'company_id', 'organisation_id')
        db.rename_column('bdr_registry_person', 'company_id', 'organisation_id')
