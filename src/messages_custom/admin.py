# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

"""Configuration of the admin application.
"""


from django.contrib import admin
from messages_custom import models


class MailTemplateParamAdmin(admin.ModelAdmin):
    search_fields = ('pattern',)
    list_display = ('pattern',)
    list_filter = ('pattern',)


class MailTemplateAdmin(admin.ModelAdmin):
    search_fields = ('name', 'type')
    list_display = ('name', 'content', 'type', 'default', 'description')


class MessageProfileAdmin(admin.ModelAdmin):
    list_display = ('message', 'ocl')


admin.site.register(models.MailTemplateParam, MailTemplateParamAdmin)
admin.site.register(models.MailTemplate, MailTemplateAdmin)
admin.site.register(models.MessageProfile, MessageProfileAdmin)


# vim: set et sw=4 ts=4 sts=4 tw=78:
