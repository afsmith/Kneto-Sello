from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import models as auth_models
from datetime import datetime
import logging
import os, shutil, subprocess, tempfile
import re
from content.models import Course

import re, time
class Report(models.Model):
    
    FORMAT_PDF = 0
    FORMAT_HTML = 1
    
    FORMAT_TYPES = (
        (FORMAT_PDF, _('PDF')),
        (FORMAT_HTML, _('HTML'))                
    )
    
    SCHEDULE_ONDEMAND   = 0
    SCHEDULE_WEEKLY     = 1
    SCHEDULE_MONTHLY    = 2
    SCHEDULE_DAILY      = 3

    SCHEDULE_TYPE_ONDEMAND = _('On demand')
    SCHEDULE_TYPE_DAILY = _('Once a day')
    SCHEDULE_TYPE_WEEKLY = _('Once a week')
    SCHEDULE_TYPE_MONTHLY = _('Once a month')

    SCHEDULE_TYPES = {
        SCHEDULE_ONDEMAND: SCHEDULE_TYPE_ONDEMAND,
        SCHEDULE_DAILY: SCHEDULE_TYPE_DAILY,
        SCHEDULE_WEEKLY: SCHEDULE_TYPE_WEEKLY,
        SCHEDULE_MONTHLY: SCHEDULE_TYPE_MONTHLY,
    }
    
    SCHEDULE_TYPES_CHOICES = (
        (SCHEDULE_ONDEMAND, SCHEDULE_TYPE_ONDEMAND),
        (SCHEDULE_DAILY, SCHEDULE_TYPE_DAILY),
        (SCHEDULE_WEEKLY, SCHEDULE_TYPE_WEEKLY),
        (SCHEDULE_MONTHLY, SCHEDULE_TYPE_MONTHLY),
    )
        
    name = models.CharField(_('Name'), max_length=100, null=False)
    template_path = models.CharField(_('Template'), max_length=128, null=True)
    created_on = models.DateTimeField(_('Creation date'), auto_now_add=True)
    modified_on = models.DateTimeField(_('Modification date'), auto_now=True)
    executed_on = models.DateTimeField(_('Last run'), null=True, default=None)
    note = models.CharField(_('Note'), max_length=400, null=True)    
    owner = models.ForeignKey(auth_models.User, null=True)
    schedule_type = models.IntegerField(_('Schedule'), choices=SCHEDULE_TYPES_CHOICES, default=SCHEDULE_ONDEMAND)
    schedule_day = models.IntegerField(_('Run on'), default=1)
    schedule_hour = models.CharField(_('Run hour'), max_length=5, default='00:00', null=True)
    user = models.ForeignKey(auth_models.User, null=True, related_name='+')
    group = models.ForeignKey(auth_models.Group, null=True)
    course = models.ForeignKey(Course, null=True)
    admin = models.ForeignKey(auth_models.User, null=True, related_name='+')
    date_from = models.DateTimeField(null=True)
    date_to = models.DateTimeField(null=True)
    
    user_required = models.BooleanField(null=False, default=False)
    group_required = models.BooleanField(null=False, default=False)
    course_required = models.BooleanField(null=False, default=False)
    admin_required = models.BooleanField(null=False, default=False)
    
    user_shown = models.BooleanField(null=False, default=False)
    group_shown = models.BooleanField(null=False, default=False)
    course_shown = models.BooleanField(null=False, default=False)
    admin_shown = models.BooleanField(null=False, default=False)
    
    date_from_shown = models.BooleanField(null=False, default=False)
    date_to_shown = models.BooleanField(null=False, default=False)
    
    is_template = models.BooleanField(null=False, default=False)
    is_deleted = models.BooleanField(null=False, default=False)

    show_all = models.BooleanField(null=False, default=False)
    use_webservice = models.BooleanField(null=False, default=False)
    
    def clean_template_name(self, old_name):
        return re.sub(r'[^A-Za-z0-9_.]+', '_', old_name.replace('.', '{0}.'.format(int(time.time()))))
 
    def is_runnable(self):
        if self.schedule_type:
            now = datetime.now()
            schedule_hour = datetime.strptime(self.schedule_hour, "%H:%M")
            if self.schedule_type == Report.SCHEDULE_WEEKLY:
                return self.schedule_day == now.weekday() and self.executed_on.weekday() != now.weekday() and schedule_hour <= now
            elif self.schedule_type == Report.SCHEDULE_MONTHLY:
                return self.schedule_day == now.day and self.executed_on.weekday() != now.weekday() and schedule_hour <= now
            elif self.schedule_type == Report.SCHEDULE_DAILY:
                return schedule_hour <= now

    def uses_webservice(self):
        with open(os.path.join(settings.REPORTS_TEMPLATES_DIR, self.template_path), 'r') as file:
            for line in file.readlines():
                matched = re.match('\s*<property\s+name="WEBSERVICE"\s+value="(?P<webservice>.+)"/>.*', line)
                if matched:
                    if matched.group('webservice').lower() == 'true':
                        return True
            return False
   
    def __str__(self):
        return self.name.encode('utf-8')

   
class ReportResult(models.Model):
    
    STATUS_SUCCESS  = 0
    STATUS_FAIL     = 1    
    
    STATUS_TYPES = (        
        (STATUS_SUCCESS,   _('Report generated successfully')),
        (STATUS_FAIL, _('Report generation failed'))
    )
    
    report = models.ForeignKey(Report)
    file_path = models.CharField(_('File'), max_length=128, null=True, default=None)
    html_file_path = models.CharField(_('File'), max_length=128, null=True, default=None)
    created_on = models.DateTimeField(_('Creation date'), auto_now_add=True)
    status = models.IntegerField(_('Status'), choices=STATUS_TYPES)


    