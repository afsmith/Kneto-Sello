# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#     Bartosz Oler <bartosz.oler@blstream.com>
#

"""URL dispatcher configuration for the app.
"""

from django.conf.urls.defaults import *

from administration import views


urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='administration-dashboard'),
    url(r'^ldap-config/$', views.ldap_json, name='administration-ldap_config'),
    url(r'^mycontent/$', views.mycontent_stats, name='administration-mycontent'),
    url(r'^mygroups/$', views.mygroups_stats, name='administration-mygroups'),
    url(r'^myreports/$', views.myreports_stats, name='administration-myreports'),
    url(r'^mymodules/$', views.mymodules_stats, name='administration-mymodules'),
    url(r'^mytemplates/$', views.mytemplates_stats, name='administration-mytemplates'),
    url(r'^tools/$', views.administrative_tools, name='administration-tools'),
    url(r'^adm_tools/$', views.adm_tools_site, name='administration-tools-site'),
    url(r'^self-register-settings/$', views.self_register_settings,
        name='administration-self-register-settings'),
    url(r'^ldap/$', views.ldap_settings, name='administration-ldap'),
    url(r'^content-settings/$', views.content_settings, name='administration-content-settings'),
    url(r'^gui-settings/$', views.gui_settings, name='administration-gui-settings'),
    url(r'^ldap-groups/$', views.ldap_groups, name='administration-ldap_groups'),
    url(r'^reports/$', views.reports, name='administration-reports'),
    url(r'^reports/list/$', views.reports_list, name='administration-reports-list'),
    url(r'^reports/create/$', views.reports_create, name='administration-reports-create'),
    url(r'^reports/create/(?P<id>\d+)/$', views.reports_create, name='administration-reports-edit'),
    url(r'^reports/delete/(?P<id>\d+)/$', views.reports_delete, name='administration-reports-delete'),
)


# vim: set et sw=4 ts=4 sts=4 tw=78:
