# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DownloadEvent'
        db.create_table('content_downloadevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Segment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('download_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('content', ['DownloadEvent'])


    def backwards(self, orm):
        
        # Deleting model 'DownloadEvent'
        db.delete_table('content_downloadevent')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'content.collection': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Collection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'content.collectionelem': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CollectionElem'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Collection']"}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.File']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {})
        },
        'content.course': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_download': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_skipping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deactivated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'through': "orm['content.CourseGroup']", 'symmetrical': 'False'}),
            'groups_can_be_assigned_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'course_can_assign'", 'symmetrical': 'False', 'through': "orm['content.CourseGroupCanBeAssignedTo']", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'objective': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'state_code': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'content.coursegroup': {
            'Meta': {'object_name': 'CourseGroup'},
            'assigned_on': ('django.db.models.fields.DateField', [], {}),
            'assigner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Course']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'content.coursegroupcanbeassignedto': {
            'Meta': {'object_name': 'CourseGroupCanBeAssignedTo'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Course']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'content.downloadevent': {
            'Meta': {'object_name': 'DownloadEvent'},
            'download_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Segment']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delete_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_downloadable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'f84OnVpLr9FktvlIOAzD6y'", 'unique': 'True', 'max_length': '22'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'pages_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'subkey_conv': ('django.db.models.fields.CharField', [], {'default': "'74Vri'", 'max_length': '5'}),
            'subkey_orig': ('django.db.models.fields.CharField', [], {'default': "'dNuB8'", 'max_length': '5'}),
            'subkey_preview': ('django.db.models.fields.CharField', [], {'default': "'50NPc'", 'max_length': '5'}),
            'subkey_thumbnail': ('django.db.models.fields.CharField', [], {'default': "'yXZdF'", 'max_length': '5'}),
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
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['content']
