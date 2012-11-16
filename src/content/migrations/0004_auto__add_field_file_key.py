# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from content import utils


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'File.key'
        db.add_column('content_file', 'key', self.gf('django.db.models.fields.CharField')(default=utils.gen_file_key, unique=True, max_length=22), keep_default=False)

    def backwards(self, orm):
        # Deleting field 'File.key'
        db.delete_column('content_file', 'key')


    models = {
        'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "utils.gen_file_key", 'unique': 'True', 'max_length': '22'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['content']
