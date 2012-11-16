# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ConfigEntry'
        db.create_table('administration_configentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('config_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('config_val', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('administration', ['ConfigEntry'])

        # Adding model 'LDAPGroupConfig'
        db.create_table('administration_ldapgroupconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('group_dn', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('administration', ['LDAPGroupConfig'])


    def backwards(self, orm):
        
        # Deleting model 'ConfigEntry'
        db.delete_table('administration_configentry')

        # Deleting model 'LDAPGroupConfig'
        db.delete_table('administration_ldapgroupconfig')


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
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['administration']
