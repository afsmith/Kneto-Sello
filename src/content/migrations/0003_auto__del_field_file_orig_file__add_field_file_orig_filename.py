# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'File.orig_file'
        db.delete_column('content_file', 'orig_file')

        # Adding field 'File.orig_filename'
        db.add_column('content_file', 'orig_filename', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=255), keep_default=False)

        orm.File.objects.all().delete()

    def backwards(self, orm):
        
        orm.File.objects.all().delete()

        # Adding field 'File.orig_file'
        db.add_column('content_file', 'orig_file', self.gf('django.db.models.fields.files.FileField')(default='', max_length=100), keep_default=False)

        # Deleting field 'File.orig_filename'
        db.delete_column('content_file', 'orig_filename')


    models = {
        'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['content']
