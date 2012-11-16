# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'LDAPGroupConfig.is_admin'
        db.delete_column('administration_ldapgroupconfig', 'is_admin')


    def backwards(self, orm):
        
        # Adding field 'LDAPGroupConfig.is_admin'
        db.add_column('administration_ldapgroupconfig', 'is_admin', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    models = {
        'administration.configentry': {
            'Meta': {'object_name': 'ConfigEntry'},
            'config_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'config_val': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'administration.ldapgroupconfig': {
            'Meta': {'object_name': 'LDAPGroupConfig'},
            'group_dn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['administration']
