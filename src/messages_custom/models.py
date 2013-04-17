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
from messages.models import Message
from content.models import Course
from django.contrib.auth import models as auth_models

class MessageProfile(models.Model):
    message = models.ForeignKey(Message)
    courses = models.ManyToManyField(Course, null=True)
    ocl = models.ForeignKey('management.OneClickLinkToken', null=True)
    header_message_id = models.CharField(max_length=100, null=False,
            default=False, unique=True)
    header_in_reply_to = models.CharField(max_length=100, null=False,
            default=False, db_index=True)


class MailTemplateParam(models.Model):

    pattern = models.CharField(max_length=50)


class MailTemplate(models.Model):

    MSG_STATUSES = (
        (u'T', u'Send'),
        (u'F', u'Don\'t send'),
        (u'D', u'Disabled'),
    )
    TYPE_INTERNAL = 'INT'
    TYPE_EMAIL = 'EMAIL'
    TYPE_NAMES = {
        TYPE_INTERNAL: 'internal',
        TYPE_EMAIL: 'email'
    }

    MSG_IDENT_WELCOME = 'WELCOME'
    MSG_IDENT_WELCOME_GROUP = 'WELCOME_GROUP'
    MSG_IDENT_WELCOME_OCL = 'WELCOME_OCL'
    MSG_IDENT_GOODBYE = 'GOODBYE'
    MSG_IDENT_PASSWORD = 'PASSWORD'
    MSG_IDENT_DATA_EDIT = 'EDIT_DATA'
    MSG_IDENT_RECEIVE_RIGHT = 'ADD_RIGHT'
    MSG_IDENT_ADD_ASSIGNMENT = 'ADD_ASSIGNMENT'
    MSG_IDENT_ADD_ASSIGNMENT_OCL = 'ADD_ASSIGNMENT_OCL'
    MSG_IDENT_REPORT_GENERATION = "REPORT_GENERATION"
    MSG_IDENT_ADD_MULTI_ASSIGNMENTS = 'ADD_MULTI_ASSIGNMENTS'

    ONE_CLICK_LINK = "http://%s/accounts/ocl/?token=%s"
    ONE_CLICK_LINK_SMM = "http://%s/content/view_smm/%d/?token=%s"

    name = models.CharField(max_length=50)
    content = models.CharField(max_length=4096)
    subject = models.CharField(max_length=255)
    default_subject = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    default = models.CharField(max_length=4096)
    description = models.CharField(max_length=255)
    params = models.ManyToManyField(MailTemplateParam, blank=True)
    identifier = models.CharField(max_length=50)
    send_msg = models.CharField(max_length=2, choices=MSG_STATUSES)
    owner = models.ForeignKey(auth_models.User, null=True)

    @property
    def type_name(self):
        return self.TYPE_NAMES[self.type]

    @property
    def name_with_type(self):
        return ''.join([self.name, '\n(', self.type_name, ')'])

    class Meta:
        ordering = ('name', 'type',)

    @classmethod
    def for_user(cls, user, **kwargs):
        all_tmpl = list(cls.objects.filter(owner=None, **kwargs))
        if user is not None:
            by_ident = dict(((t.type, t.identifier), t) for t in cls.objects.filter(owner=user, **kwargs))
            all_tmpl = [by_ident.get((t.type, t.identifier), t) for t in all_tmpl]
        return all_tmpl

    def get_defaults(self):
        """ Get default subject and content as (subject, content)
        tuple. If it's a user modified template, return its parent
        global template defaults.
        """
        if self.owner is not None:
            tmpl = MailTemplate.objects.get(type=self.type, identifier=self.identifier, owner=None)
            return tmpl.subject, tmpl.content
        return self.default_subject, self.default

    def get_params(self):
        if self.owner is not None:
            tmpl = MailTemplate.objects.get(type=self.type, identifier=self.identifier, owner=None)
            return tmpl.params
        return self.params

    def populate_params(self, params_dict):
        return self.populate_params_to_text(self.content, params_dict)

    def populate_params_to_text(self, text, params_dict):
        if params_dict:
            for key, val in params_dict.items():
                text = text.replace(key, val)

        return text

# vim: set et sw=4 ts=4 sts=4 tw=78:
