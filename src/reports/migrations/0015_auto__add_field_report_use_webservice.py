# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Report.use_webservice'
        db.add_column('reports_report', 'use_webservice', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)
        for report in orm.Report.objects.all():
            report.use_webservice = True
            report.save()


    def backwards(self, orm):
        
        # Deleting field 'Report.use_webservice'
        db.delete_column('reports_report', 'use_webservice')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'reports.report': {
            'Meta': {'object_name': 'Report'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'admin_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'admin_shown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Course']", 'null': 'True'}),
            'course_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'course_shown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_from_shown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_to_shown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'executed_on': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True'}),
            'group_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group_shown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_template': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'schedule_day': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'schedule_hour': ('django.db.models.fields.CharField', [], {'default': "'00:00'", 'max_length': '5', 'null': 'True'}),
            'schedule_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template_path': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'use_webservice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_shown': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'reports.reportresult': {
            'Meta': {'object_name': 'ReportResult'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_path': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True'}),
            'html_file_path': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reports.Report']"}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['reports']
