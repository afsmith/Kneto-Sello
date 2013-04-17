# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.core.management import call_command

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'MailTemplate.default_subject'
        db.add_column('messages_custom_mailtemplate', 'default_subject', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)

    def backwards(self, orm):
        
        # Deleting field 'MailTemplate.default_subject'
        db.delete_column('messages_custom_mailtemplate', 'default_subject')


    models = {
        'messages_custom.mailtemplate': {
            'Meta': {'ordering': "('name', 'type')", 'object_name': 'MailTemplate'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'default_subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'params': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['messages_custom.MailTemplateParam']", 'symmetrical': 'False', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'messages_custom.mailtemplateparam': {
            'Meta': {'object_name': 'MailTemplateParam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['messages_custom']
