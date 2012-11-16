# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

""" Models for administrative settings.
"""
from django.conf import settings
from django.core.files.uploadhandler import MemoryFileUploadHandler, FileUploadHandler, StopUpload, UploadFileException, StopFutureHandlers, TemporaryFileUploadHandler

import ldap

from django.db import models
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext_lazy as _


class ConfigEntry(models.Model):

    AUTH_LDAP_IS_USED = 'AUTH_LDAP_IS_USED'
    AUTH_LDAP_SERVER_URI = 'AUTH_LDAP_SERVER_URI'
    AUTH_LDAP_USERS_DN = 'AUTH_LDAP_USERS_DN'
    AUTH_LDAP_GROUPS_DN = 'AUTH_LDAP_GROUPS_DN'
    AUTH_LDAP_USER_DISCRIMINANT = 'AUTH_LDAP_USER_DISCRIMINANT'
    AUTH_LDAP_GROUP_TYPE = 'AUTH_LDAP_GROUP_TYPE'
    AUTH_LDAP_GROUP_OBJECT_CLASS = 'AUTH_LDAP_GROUP_OBJECT_CLASS'

    AUTH_LDAP_FIRST_NAME_MAPPING = 'AUTH_LDAP_FIRST_NAME_MAPPING'
    AUTH_LDAP_LAST_NAME_MAPPING = 'AUTH_LDAP_LAST_NAME_MAPPING'
    AUTH_LDAP_EMAIL_MAPPING = 'AUTH_LDAP_EMAIL_MAPPING'
    AUTH_LDAP_PHONE_MAPPING = 'AUTH_LDAP_PHONE_MAPPING'


    AUTH_LDAP_CONFIGS = [AUTH_LDAP_IS_USED,
                        AUTH_LDAP_SERVER_URI,
                        AUTH_LDAP_USERS_DN,
                        AUTH_LDAP_GROUPS_DN,
                        AUTH_LDAP_USER_DISCRIMINANT,
                        AUTH_LDAP_GROUP_TYPE,
                        AUTH_LDAP_GROUP_OBJECT_CLASS]

    AUTH_LDAP_USER_ATTRS = [AUTH_LDAP_FIRST_NAME_MAPPING,
                                 AUTH_LDAP_LAST_NAME_MAPPING,
                                 AUTH_LDAP_EMAIL_MAPPING,
                                 AUTH_LDAP_PHONE_MAPPING]

    AUTH_LDAP_USER_ATTRS_MAP = {
        AUTH_LDAP_FIRST_NAME_MAPPING: 'first_name',
        AUTH_LDAP_LAST_NAME_MAPPING: 'last_name',
        AUTH_LDAP_EMAIL_MAPPING: 'email',
        AUTH_LDAP_PHONE_MAPPING: 'phone'
    }

    GROUP_TYPE_POSIX_GROUP = 'posixGroup'
    GROUP_TYPE_GROUP_OF_NAMES = 'groupOfNames'
    GROUP_TYPE_GROUP_OF_UNIQUE_NAMES = 'groupOfUniqueNames'
    GROUP_TYPE_ACTIVE_DIRECTORY_GROUP = 'activeDirectoryGroup'

    GROUPS_TYPES = (
        (GROUP_TYPE_ACTIVE_DIRECTORY_GROUP, 'activeDirectoryGroup'),
        (GROUP_TYPE_GROUP_OF_NAMES, 'groupOfNames'),
        (GROUP_TYPE_GROUP_OF_UNIQUE_NAMES, 'groupOfUniqueNames'),
        (GROUP_TYPE_POSIX_GROUP, 'posixGroup')
    )

    GROUPS_CLASSES = {
        GROUP_TYPE_POSIX_GROUP: 'PosixGroupType',
        GROUP_TYPE_GROUP_OF_NAMES: 'GroupOfNamesType',
        GROUP_TYPE_GROUP_OF_UNIQUE_NAMES: 'GroupOfUniqueNamesType',
        GROUP_TYPE_ACTIVE_DIRECTORY_GROUP: 'ActiveDirectoryGroupType'
    }

    QUALITY_TYPE_HIGH = 'highQuality'
    QUALITY_TYPE_MEDIUM = 'mediumQuality'
    QUALITY_TYPE_LOW = 'lowQuality'

    QUALITY_TYPES = (
        (QUALITY_TYPE_HIGH, _('high')),
        (QUALITY_TYPE_MEDIUM, _('medium')),
        (QUALITY_TYPE_LOW, _('low')),
    )

    CONTENT_QUALITY_OF_CONTENT = 'CONTENT_QUALITY_OF_CONTENT'
    CONTENT_USE_DMS = 'CONTENT_USE_DMS'
    CONTENT_DMS_PATH = 'CONTENT_DMS_PATH'
    CONTENT_URL_FOR_LOCAL_MEDIA_SERVER = 'CONTENT_URL_FOR_LOCAL_MEDIA_SERVER'

    GUI_DEFAULT_LANGUAGE = 'GUI_DEFAULT_LANGUAGE'
    GUI_CUSTOM_WEB_TITLE = 'GUI_CUSTOM_WEB_TITLE'
    GUI_FOOTER = 'GUI_FOOTER'
    GUI_CSS_FILE = 'GUI_CSS_FILE'   
    
    GUI_APPLICATION_ICONS = 'GUI_APPLICATION_ICONS'
    GUI_FILETYPE_ICONS = 'GUI_FILETYPE_ICONS'
    GUI_PROGRESS_ICONS = 'GUI_PROGRESS_ICONS'
    GUI_MAIN_MENU_BAR = 'GUI_MAIN_MENU_BAR'
    
    SELF_REGISTER_TOKEN = 'SELF_REGISTER_TOKEN'

    config_key = models.CharField(_('Config entry name'), max_length=255, unique=True)
    config_val = models.CharField(_('Config entry value'), max_length=255)

def _get_quality_type_label(type):
    for tuple in ConfigEntry.QUALITY_TYPES:
        if tuple[0] == type:
            return unicode(tuple[1])
    return

def get_entry(key):
    """
        Searches for ConfigEntry instance matching given key.

        :param key - key which is supposed to be searched

        :returns ConfigEntry from database matching given key or
                 None if no match was made.
    """
    try:
        return ConfigEntry.objects.get(config_key=key)
    except ConfigEntry.DoesNotExist:
        return None

def get_entry_val(key):
    try:
        return ConfigEntry.objects.get(config_key=key).config_val
    except ConfigEntry.DoesNotExist:
        return None

class LDAPGroupConfig(models.Model):
    name = models.CharField(_('Local group name'), max_length=255)
    group_dn = models.CharField(_('LDAP group DN'), max_length=255, unique=True)

class MaxFileMemoryFileUploadHandler(MemoryFileUploadHandler):

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        if content_length > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            self.activated = False
        else:
            self.activated = True

class MaxFileTemporaryFileUploadHandler(TemporaryFileUploadHandler):

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        if content_length > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            self.activated = False
        else:
            self.activated = True

    def new_file(self, file_name, *args, **kwargs):
        if self.activated:
            super(MaxFileTemporaryFileUploadHandler, self).new_file(file_name, *args, **kwargs)

    def receive_data_chunk(self, raw_data, start):
        if self.activated:
            super(MaxFileTemporaryFileUploadHandler, self).receive_data_chunk(raw_data, start)

    def file_complete(self, file_size):
        if self.activated:
            super(MaxFileTemporaryFileUploadHandler, self).file_complete(file_size)
        else:
            return
        
