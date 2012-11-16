# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Course'
        db.create_table('content_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('objective', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('content', ['Course'])

        # Adding model 'Segment'
        db.create_table('content_segment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.File'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Course'])),
            ('track', self.gf('django.db.models.fields.IntegerField')()),
            ('start', self.gf('django.db.models.fields.IntegerField')()),
            ('end', self.gf('django.db.models.fields.IntegerField')()),
            ('playback_mode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('content', ['Segment'])


    def backwards(self, orm):
        
        # Deleting model 'Course'
        db.delete_table('content_course')

        # Deleting model 'Segment'
        db.delete_table('content_segment')


    models = {
        'content.course': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Course'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'objective': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'segments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['content.File']", 'through': "orm['content.Segment']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'GcAktSAW6GUuX1cuVMm7K'", 'unique': 'True', 'max_length': '22'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'content.segment': {
            'Meta': {'ordering': "('course', 'start', 'track')", 'object_name': 'Segment'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Course']"}),
            'end': ('django.db.models.fields.IntegerField', [], {}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.File']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playback_mode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.IntegerField', [], {}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['content']
