# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

""" Serializers for models from administrative settings.
"""

from models import LDAPGroupConfig

def serialize_ldap_group_config(groupConfig):
    return {'id': groupConfig.id,
            'name':groupConfig.name,
            'group_dn':groupConfig.group_dn}

