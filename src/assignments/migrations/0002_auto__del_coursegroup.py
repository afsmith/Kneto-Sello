# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'CourseGroup'
        db.delete_table('assignments_coursegroup')


    def backwards(self, orm):
        
        # Adding model 'CourseGroup'
        db.create_table('assignments_coursegroup', (
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Course'])),
            ('assign_date', self.gf('django.db.models.fields.DateField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('assignments', ['CourseGroup'])


    models = {
        
    }

    complete_apps = ['assignments']
