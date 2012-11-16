# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('content_coursegroup', 'user_id', 'assigner_id')

    def backwards(self, orm):
        db.rename_column('content_coursegroup', 'assigner_id', 'user_id')
