# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'MessageProfile.ocls'
        db.add_column('messages_custom_messageprofile', 'ocls', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management.OneClickLinkToken'], null=True), keep_default=False)

        # Removing M2M table for field ocls on 'MessageProfile'
        db.delete_table('messages_custom_messageprofile_ocls')


    def backwards(self, orm):
        
        # Deleting field 'MessageProfile.ocls'
        db.delete_column('messages_custom_messageprofile', 'ocls_id')

        # Adding M2M table for field ocls on 'MessageProfile'
        db.create_table('messages_custom_messageprofile_ocls', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messageprofile', models.ForeignKey(orm['messages_custom.messageprofile'], null=False)),
            ('oneclicklinktoken', models.ForeignKey(orm['management.oneclicklinktoken'], null=False))
        ))
        db.create_unique('messages_custom_messageprofile_ocls', ['messageprofile_id', 'oneclicklinktoken_id'])


    models = {
        'auth.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
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
            'Meta': {'ordering': "['first_name', 'last_name']", 'object_name': 'User'},
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'content.course': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_download': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_skipping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completion_msg': ('django.db.models.fields.TextField', [], {'default': "'Lesson finished'", 'null': 'True', 'blank': 'True'}),
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
            'sign_off_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        'management.oneclicklinktoken': {
            'Meta': {'object_name': 'OneClickLinkToken'},
            'allow_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'kWzkzH2FoYZD16hZICKms6CXR9H4Pb'", 'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'messages.message': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_messages'", 'null': 'True', 'to': "orm['messages.Message']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'received_messages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'recipient_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'replied_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': "orm['auth.User']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'messages_custom.mailtemplate': {
            'Meta': {'ordering': "('name', 'type')", 'object_name': 'MailTemplate'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'default_subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'params': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['messages_custom.MailTemplateParam']", 'symmetrical': 'False', 'blank': 'True'}),
            'send_msg': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'messages_custom.mailtemplateparam': {
            'Meta': {'object_name': 'MailTemplateParam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'messages_custom.messageprofile': {
            'Meta': {'object_name': 'MessageProfile'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['content.Course']", 'null': 'True', 'symmetrical': 'False'}),
            'header_in_reply_to': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '100', 'db_index': 'True'}),
            'header_message_id': ('django.db.models.fields.CharField', [], {'default': 'False', 'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['messages.Message']"}),
            'ocls': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['management.OneClickLinkToken']", 'null': 'True'})
        }
    }

    complete_apps = ['messages_custom']
