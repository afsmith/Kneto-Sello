# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MailTemplateParam'
        db.create_table('messages_custom_mailtemplateparam', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pattern', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('messages_custom', ['MailTemplateParam'])

        # Adding model 'MailTemplate'
        db.create_table('messages_custom_mailtemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('messages_custom', ['MailTemplate'])

        # Adding M2M table for field params on 'MailTemplate'
        db.create_table('messages_custom_mailtemplate_params', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mailtemplate', models.ForeignKey(orm['messages_custom.mailtemplate'], null=False)),
            ('mailtemplateparam', models.ForeignKey(orm['messages_custom.mailtemplateparam'], null=False))
        ))
        db.create_unique('messages_custom_mailtemplate_params', ['mailtemplate_id', 'mailtemplateparam_id'])


    def backwards(self, orm):
        
        # Deleting model 'MailTemplateParam'
        db.delete_table('messages_custom_mailtemplateparam')

        # Deleting model 'MailTemplate'
        db.delete_table('messages_custom_mailtemplate')

        # Removing M2M table for field params on 'MailTemplate'
        db.delete_table('messages_custom_mailtemplate_params')


    models = {
        'messages_custom.mailtemplate': {
            'Meta': {'ordering': "('name', 'type')", 'object_name': 'MailTemplate'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'params': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['messages_custom.MailTemplateParam']", 'symmetrical': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'messages_custom.mailtemplateparam': {
            'Meta': {'object_name': 'MailTemplateParam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['messages_custom']
