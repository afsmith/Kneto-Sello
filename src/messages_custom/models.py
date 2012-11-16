# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

"""Models for messaging component.
"""

from django.db import models


class MailTemplateParam(models.Model):

    pattern = models.CharField(max_length=50)

    
class MailTemplate(models.Model):

    TYPE_INTERNAL = 'INT'
    TYPE_EMAIL = 'EMAIL'
    TYPE_NAMES = {
        TYPE_INTERNAL: 'internal',
        TYPE_EMAIL: 'email'
    }

    MSG_IDENT_WELCOME = 'WELCOME'
    MSG_IDENT_WELCOME_OCL = 'WELCOME_OCL'
    MSG_IDENT_GOODBYE = 'GOODBYE'
    MSG_IDENT_PASSWORD = 'PASSWORD'
    MSG_IDENT_DATA_EDIT = 'EDIT_DATA'
    MSG_IDENT_RECEIVE_RIGHT = 'ADD_RIGHT'
    MSG_IDENT_ADD_ASSIGNMENT = 'ADD_ASSIGNMENT'
    MSG_IDENT_ADD_ASSIGNMENT_OCL = 'ADD_ASSIGNMENT_OCL'
    MSG_IDENT_REPORT_GENERATION = "REPORT_GENERATION"

    ONE_CLICK_LINK = "http://%s/accounts/ocl/?token=%s"

    name = models.CharField(max_length=50)
    content = models.CharField(max_length=1024)
    subject = models.CharField(max_length=255)
    default_subject = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    default = models.CharField(max_length=1024)
    description = models.CharField(max_length=255)
    params = models.ManyToManyField(MailTemplateParam, blank=True)
    identifier = models.CharField(max_length=50)

    @property
    def type_name(self):
        return self.TYPE_NAMES[self.type]

    @property
    def name_with_type(self):
        return ''.join([self.name,'\n(',self.type_name,')'])

    class Meta:
        ordering = ('name', 'type',)

    def populate_params(self, params_dict):
        return self.populate_params_to_text(self.content, params_dict)

    def populate_params_to_text(self, text, params_dict):
        if params_dict:
            for key, val in params_dict.items():
                text = text.replace(key, val)

        return text


# vim: set et sw=4 ts=4 sts=4 tw=78: