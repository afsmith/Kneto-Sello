# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

""" Utils for administrative settings.
"""

import ldap
from ldap.dn import str2dn

from django.contrib.auth import models as auth_models

from ldap_backend import backend
from management import models as manage_models
from models import get_entry, ConfigEntry, LDAPGroupConfig


class LDAPSynchError(Exception):
    def __init__(self, msg):
        self._msg = msg

    def get_error_msg(self):
        return self._msg
    

class LDAPSynchronizer(object):

    def __init__(self):
        self._ldap_config = backend.ldap_settings
        self._ldap_config.__init__()
        self._user_discriminant = get_entry(ConfigEntry.AUTH_LDAP_USER_DISCRIMINANT)
        self._groups_dn = get_entry(ConfigEntry.AUTH_LDAP_GROUPS_DN)
        self._group_type = get_entry(ConfigEntry.AUTH_LDAP_GROUP_OBJECT_CLASS)
        if not self._group_type:
            raise LDAPSynchError('No group type specified')

        self._members_info = get_members_info(self._group_type.config_val)

        try:
            self._connection = ldap.initialize(self._ldap_config.AUTH_LDAP_SERVER_URI)
        except ldap.LDAPError, e:
            raise LDAPSynchError(e.args[0]['desc'])

    def synchronize_group(self, group_dn, group_name):
        found, group_data = self._find_group(group_dn)

        if found:
            group, _ = auth_models.Group.objects.get_or_create(name=group_name)

            # clear user of ldap groups
            for user in auth_models.User.objects.filter(groups__name=group_name,
                                                        userprofile__ldap_user=True):
                for group in user.groups.filter(name__in=LDAPGroupConfig.objects.all().values('name')):
                    user.groups.remove(group)
                user.save()
                #user.groups -=
                #for group_conf in LDAPGroupConfig.objects.all():

                #if group in user.groups.all():
                #    user.groups.remove(group)
                #    user.save()
            # clear user of ldap groups

            for member in group_data[1][self._members_info['usersField']]:
                user_found, ldap_user = self._find_user(member)
                if user_found:
                    db_user, user_created = auth_models.User.objects.get_or_create(username=ldap_user[1][self._user_discriminant.config_val][0])
                    if user_created or db_user.get_profile().ldap_user:
                        self._populate_user_from_attributes(user=db_user, ldap_data=ldap_user[1])

                        db_user.set_unusable_password()
                        db_user.save()

                        if user_created:
                            profile = manage_models.UserProfile(user=db_user,
                                                                ldap_user=True,
                                                                role=manage_models.UserProfile.ROLE_USER)
                        else:
                            profile = db_user.get_profile()
                        if profile.role not in [manage_models.UserProfile.ROLE_ADMIN,
                                                manage_models.UserProfile.ROLE_SUPERADMIN]:
                            profile.role = manage_models.UserProfile.ROLE_USER
                        self._populate_profile_fields(profile=profile, ldap_data=ldap_user[1])
                        profile.save()

                        groups_found, user_groups = self._find_user_groups(ldap_user[0],ldap_user[1])
                        #groups_set = set([])
                        for group in user_groups:
                            if check_group_dn_existence(group[0]):
                                group_config = LDAPGroupConfig.objects.get(group_dn=group[0])
                                group, _ = auth_models.Group.objects.get_or_create(name=group_config.name)
                                #groups_set.add(group)
                                db_user.groups.add(group)

                        #db_user.groups = groups_set
                        db_user.save()
                    else:
                        continue
                else:
                    continue

        else:
            raise LDAPSynchError('Group with DN = %s was not found in LDAP'%group_dn)



    def _find_group(self, group_dn):

        searchFilter = "objectClass=%s"%self._group_type.config_val

        try:
            ldap_results = self._connection.search_s(group_dn, ldap.SCOPE_BASE, searchFilter, None)
            if len(ldap_results):
                return True, ldap_results[0]
            else:
                return False, 'Group %s not found'%group_dn
        except ldap.LDAPError, e:
            return False, e.args[0]['desc']

    def _find_user_groups(self, ldap_user_dn, ldap_user):
        if self._members_info['searchBy'] == 'dn':
            searchFilter = "(&(objectClass=%s)(%s=%s))"%(self._group_type.config_val,
                                                   self._members_info['usersField'],
                                                   ldap_user_dn)
        else:
            searchFilter = "(&(objectClass=%s)(%s=%s))"%(self._group_type.config_val,
                                                   self._members_info['usersField'],
                                                   ldap_user[self._user_discriminant.config_val][0])

        try:
            ldap_results = self._connection.search_s(self._groups_dn.config_val,
                                                     ldap.SCOPE_SUBTREE,
                                                     searchFilter,
                                                     None)
            return True, ldap_results
        except ldap.LDAPError, e:
            return False, e.args[0]['desc']

    def _find_user(self, user_field):

        try:
            users_base = get_entry(ConfigEntry.AUTH_LDAP_USERS_DN)

            if self._members_info['searchBy'] == 'dn':
                ldap_results = self._connection.search_s(user_field,
                                                         ldap.SCOPE_BASE,
                                                         "objectClass=*",
                                                         None)
            else:
                search_filter = "%s=%s"%(self._members_info['searchBy'], user_field)
                ldap_results = self._connection.search_s(users_base.config_val,
                                                         ldap.SCOPE_SUBTREE,
                                                         search_filter)

            if len(ldap_results):
                return True, ldap_results[0]
            else:
                return False, 'User %s not found'%user_field
        except ldap.LDAPError, e:
            return False, e.args[0]['desc']

    def _populate_user_from_attributes(self, user, ldap_data):
        for field, value in self._ldap_config.AUTH_LDAP_USER_ATTR_MAP.items():
            try:
                setattr(user, field, unicode(ldap_data[value][0],'utf-8'))
            except (KeyError, IndexError):
                pass

    def _populate_profile_fields(self, profile, ldap_data):
        for field, attr in self._ldap_config.AUTH_LDAP_USER_ATTR_MAP.iteritems():
            try:
                setattr(profile, field, unicode(ldap_data[attr][0],'utf-8'))
            except (KeyError, IndexError), e:
                pass
    

def get_members_info(group_type):

    if group_type == ConfigEntry.GROUP_TYPE_POSIX_GROUP:
        return {'searchBy': 'uid',
                'usersField': 'memberUid'}
    elif group_type == ConfigEntry.GROUP_TYPE_GROUP_OF_NAMES:
        return {'searchBy': 'dn',
                'usersField': 'member'}
    elif group_type == ConfigEntry.GROUP_TYPE_GROUP_OF_UNIQUE_NAMES:
        return {'searchBy': 'dn',
                'usersField': 'uniqueMember'}
    elif group_type == ConfigEntry.GROUP_TYPE_ACTIVE_DIRECTORY_GROUP:
        return {'searchBy': 'dn',
                'usersField': 'member'}
    else:
        raise LDAPSynchError('Unknown group type')

def check_group_dn_existence(group_dn):
    group_configs = LDAPGroupConfig.objects.all()
    if str2dn(group_dn) in [str2dn(group_conf.group_dn) for group_conf in group_configs]:
        return True
    return False

def check_group_name_existence(name):
    try:
        group = auth_models.Group.objects.get(name=name)
        return True
    except auth_models.Group.DoesNotExist:
        return False

def validate_dn_format(group_dn):
    try:
        str2dn(group_dn)
        return True
    except ldap.LDAPError:
        return False
