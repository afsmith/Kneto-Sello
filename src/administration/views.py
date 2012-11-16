# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#
#

"""Django views.
"""
from django.db.models import Count
from django.db.models.query_utils import Q

from administration import forms, models, serializers, forms, models, \
    serializers
from administration.models import ConfigEntry, _get_quality_type_label, get_entry, get_entry_val
from administration.nginx_config import NginxConfig
from bls_common import bls_django
from contextlib import closing
from django import http, http
from django.conf import settings
from django.contrib.auth import models as auth_models, models as auth_models
from django.core.files import storage, uploadedfile
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.db import models as db_models
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template, direct_to_template

from ldap.dn import dn2str, str2dn
from content.course_states import Draft, Active, ActiveAssign, ActiveInUse, Deactivated, DeactivatedUsed, Removed
from content.models import File, Course
from management import models as manage_models
from plato_common import decorators, decorators
from reports import models as report_models
from reports.models import Report
from utils import check_group_name_existence, LDAPSynchronizer, LDAPSynchError, \
    validate_dn_format
import json
import os
import shutil

LDAP_SETTINGS_ENTRY_MAP = {'use_ldap': models.ConfigEntry.AUTH_LDAP_IS_USED,
                   'ldap_url': models.ConfigEntry.AUTH_LDAP_SERVER_URI,
                   'users_dn': models.ConfigEntry.AUTH_LDAP_USERS_DN,
                   'groups_dn': models.ConfigEntry.AUTH_LDAP_GROUPS_DN,
                   'group_type': models.ConfigEntry.AUTH_LDAP_GROUP_OBJECT_CLASS,
                   'user_discriminant': models.ConfigEntry.AUTH_LDAP_USER_DISCRIMINANT,
                   'first_name': models.ConfigEntry.AUTH_LDAP_FIRST_NAME_MAPPING,
                   'last_name': models.ConfigEntry.AUTH_LDAP_LAST_NAME_MAPPING,
                   'email': models.ConfigEntry.AUTH_LDAP_EMAIL_MAPPING,
                   'phone': models.ConfigEntry.AUTH_LDAP_PHONE_MAPPING}

CONTENT_SETTINGS_ENTRY_MAP = {'quality_of_content': models.ConfigEntry.CONTENT_QUALITY_OF_CONTENT,
                              'use_dms': models.ConfigEntry.CONTENT_USE_DMS,
                              'dms_path': models.ConfigEntry.CONTENT_DMS_PATH,}
GUI_SETTINGS_ENTRY_MAP = {'default_language': models.ConfigEntry.GUI_DEFAULT_LANGUAGE,
                          'custom_web_title': models.ConfigEntry.GUI_CUSTOM_WEB_TITLE,
                          'footer': models.ConfigEntry.GUI_FOOTER,}

SELF_REGISTER_SETTINGS_ENTRY_MAP = {'token': models.ConfigEntry.SELF_REGISTER_TOKEN}                       

GUI_SETTINGS_FILES = {'css_file': models.ConfigEntry.GUI_CSS_FILE,
                      'application_icons': models.ConfigEntry.GUI_APPLICATION_ICONS,
                      'filetype_icons': models.ConfigEntry.GUI_FILETYPE_ICONS,
                      'progress_icons': models.ConfigEntry.GUI_PROGRESS_ICONS,
                      'main_menu_bar': models.ConfigEntry.GUI_MAIN_MENU_BAR}

GUI_FILES_NAMES = {'application_icons': settings.CUSTOM_APPLICATION_ICONS_NAME,
                   'css_file':settings.CUSTOM_CSS_FILE_NAME,
                   'filetype_icons': settings.CUSTOM_FILETYPE_ICONS_NAME,
                   'progress_icons': settings.CUSTOM_PROGRESS_ICONS_NAME,
                   'main_menu_bar': settings.CUSTOM_MAIN_MENU_BAR_NAME}

GUI_FILES_NAMES_DEFAULT = {'application_icons': settings.DEFAULT_APPLICATION_ICONS_NAME,
                           'css_file':settings.DEFAULT_CSS_FILE_NAME,
                           'filetype_icons': settings.DEFAULT_FILETYPE_ICONS_NAME,
                           'progress_icons': settings.DEFAULT_PROGRESS_ICONS_NAME,
                           'main_menu_bar': settings.DEFAULT_MAIN_MENU_BAR_NAME}
                                  

BOOLEAN_ENTRIES = ['use_ldap', 'use_dms']

GROUP_EXISTS_MESSAGE = 'Group %s already exists, users from %s will be added to that group.'



def get_initial_form_values(entry_map):
    initial = {}
    for key, value in entry_map.items():
        config_object = models.get_entry(value)
        if config_object:
            val = config_object.config_val
            if key in BOOLEAN_ENTRIES:
                initial[key]= val == 'True'
            else:
                initial[key] = val
    return initial


@decorators.is_admin_or_superadmin
def dashboard(request):
    if request.user.get_profile().is_superadmin:
        ctx = {
            'widgets': ['my_content_stats', 'my_groups_stats', 'my_reports_stats', 'my_modules_stats', 'administrative_tools']
        }
    else:
        ctx = {
               'widgets': ['my_content_stats', 'my_groups_stats', 'my_modules_stats', 'my_reports_stats']
        }
    ctx["settings"] = {
        "REGISTRATION_OPEN": settings.REGISTRATION_OPEN
        }
    return direct_to_template(request, 'administration/dashboard.html', ctx)

@decorators.is_superadmin
def ldap_json(request):
    return bls_django.HttpJsonResponse(get_initial_form_values(LDAP_SETTINGS_ENTRY_MAP))

@decorators.is_superadmin
def administrative_tools(request):
    mapped_groups = _('False')
    if models.LDAPGroupConfig.objects.all().count() > 0:
        mapped_groups = _('True')
    return bls_django.HttpJsonResponse({'quality_of_content': _get_quality_type_label(models.get_entry_val(ConfigEntry.CONTENT_QUALITY_OF_CONTENT)),
                                        'use_dms': _translate(models.get_entry_val(ConfigEntry.CONTENT_USE_DMS)),
                                        'use_ldap': _translate(models.get_entry_val(ConfigEntry.AUTH_LDAP_IS_USED)),
                                        'mapped_groups': unicode(mapped_groups)})

@decorators.is_superadmin
def self_register_settings(request):
    if request.method == 'POST':
        form = forms.SelfRegisterForm(request.POST)
        if form.is_valid():
            _save_settings(form, SELF_REGISTER_SETTINGS_ENTRY_MAP)
            return bls_django.HttpResponseCreated()
    else:
        form = forms.SelfRegisterForm(initial=get_initial_form_values(
            SELF_REGISTER_SETTINGS_ENTRY_MAP))
    return direct_to_template(request,
            'administration/self_register_settings.html',
            { 'form': form,})



def _translate(value):
    if value:
        return unicode(_(value))
    return value

@decorators.is_admin_or_superadmin
def mygroups_stats(request):
    
    return bls_django.HttpJsonResponse({'total': request.user.groups.count(),
                                        'my_managed_groups': request.user.group_profiles.filter(access_level=manage_models.UserGroupProfile.LEVEL_FULL_ADMIN).count() or '0',
                                        'users_in_my_groups': auth_models.User.objects.filter(groups__in=request.user.groups.all()).count() or '0',
                                        'unique_users_in_my_groups': auth_models.User.objects.filter(groups__in=request.user.groups.all()).distinct().count() or '0',
                                        'users_in_my_managed_groups': auth_models.User.objects.filter(groups__in=request.user.group_profiles.filter(access_level=manage_models.UserGroupProfile.LEVEL_FULL_ADMIN).values_list('group')).count() or '0',
                                        'unique_users_in_my_managed_groups': auth_models.User.objects.filter(groups__in=request.user.group_profiles.filter(access_level=manage_models.UserGroupProfile.LEVEL_FULL_ADMIN).values_list('group')).distinct().count() or '0',})
@decorators.is_admin_or_superadmin
def myreports_stats(request):
    return bls_django.HttpJsonResponse({'total': Report.objects.filter(owner=request.user,is_template=False).count()})

@decorators.is_admin_or_superadmin
def mymodules_stats(request):
    total = drafts = active = deactivated = 0

    for row in Course.objects.filter(owner=request.user).values('state_code').annotate(Count('state_code')).filter(~db_models.query_utils.Q(state_code=Removed.CODE)).order_by():
        state_code = row['state_code']
        count = row['state_code__count']

        total += count
        if state_code == Draft.CODE:
            drafts = count
        elif state_code in [Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE]:
            active += count
        elif state_code in [Deactivated.CODE, DeactivatedUsed.CODE]:
            deactivated += count

    return bls_django.HttpJsonResponse({'total': total,
                                        'drafts': drafts,
                                        'active': active,
                                        'deactivated': deactivated})

@decorators.is_admin_or_superadmin
def mycontent_stats(request):
    total = audio = video = image = text = slides = scorm = 0

    for result in File.objects.filter(status__in=(File.STATUS_AVAILABLE,File.STATUS_EXPIRED),
                                      owner=request.user).\
                                      values('type').annotate(Count('type')).order_by():
        type = result['type']
        count = result['type__count']

        total += count
        if type == File.TYPE_AUDIO:
            audio = count
        elif type in [File.TYPE_PLAIN, File.TYPE_MSDOC, File.TYPE_PDF, File.TYPE_HTML]:
            text += count
        elif type == File.TYPE_VIDEO:
            video = count
        elif type == File.TYPE_SCORM:
            scorm = count
        elif type == File.TYPE_IMAGE:
            image = count
        elif type == File.TYPE_MSPPT:
            slides = count

    return bls_django.HttpJsonResponse({'total': total,
                                        'audio': audio,
                                        'video': video,
                                        'image': image,
                                        'text': text,
                                        'slides': slides,
                                        'scorm': scorm})

@decorators.is_superadmin
def content_settings(request):
    if request.method == 'POST':
        form = forms.ContentSettingsForm(request.POST)
        if form.is_valid():
            _save_settings(form, CONTENT_SETTINGS_ENTRY_MAP)
            return bls_django.HttpResponseCreated()
    else:
        form = forms.ContentSettingsForm(initial=get_initial_form_values(CONTENT_SETTINGS_ENTRY_MAP))
    return direct_to_template(request, 'administration/content_settings.html', {
        'form': form
    })

#def clean_template_name(self, old_name):
#    return re.sub(r'[^A-Za-z0-9_.]+', '_', old_name.replace('.', '{0}.'.format(int(time.time()))))


@decorators.is_superadmin
def gui_settings(request):
    if request.method == 'POST':
        form = forms.GuiSettingsForm(request.POST, request.FILES)
        try:
            data = json.loads(request.raw_post_data)
            if data['action'] == 'delete' and data['data']:
                models.ConfigEntry.objects.filter(config_key=GUI_SETTINGS_FILES[data['data']]).delete()

                shutil.copy(os.path.join(settings.CSS_TEMPLATES_DIR, GUI_FILES_NAMES_DEFAULT[data['data']]),
                            os.path.join(settings.CSS_TEMPLATES_DIR, GUI_FILES_NAMES[data['data']]))
                return http.HttpResponse("""{"status": "OK"}""")        
            
        except (TypeError, ValueError):
            pass

        if form.is_valid():
            _save_settings(form, GUI_SETTINGS_ENTRY_MAP)

            for file_name, file_key in GUI_SETTINGS_FILES.items():
                if form.cleaned_data[file_name] and type(form.cleaned_data[file_name]) is not str:
                    path = os.path.join(settings.CSS_TEMPLATES_DIR, GUI_FILES_NAMES[file_name])
                    if os.path.exists(path):
                        os.remove(path)
                    print file_name + " " + file_key
                    with closing(storage.default_storage.open(path, 'wb')) as fh:
                        for chunk in form.cleaned_data[file_name].chunks():
                            fh.write(chunk)
    
                    config_entry = get_entry(file_key)
                    if not config_entry:
                        config_entry = models.ConfigEntry(config_key=file_key)
                    config_entry.config_val=form.cleaned_data[file_name].name
                    config_entry.save()
            
    
            return http.HttpResponse("""{"status": "OK"}""")


#            
#            if form.cleaned_data['css_file'] and type(form.cleaned_data['css_file']) is not str:
#                path = os.path.join(settings.CSS_TEMPLATES_DIR, settings.CUSTOM_CSS_FILE_NAME)
#                if os.path.exists(path):
#                    os.remove(path)
#                with closing(storage.default_storage.open(path, 'wb')) as fh:
#                    for chunk in form.cleaned_data['css_file'].chunks():
#                        fh.write(chunk)
#
#                config_entry = get_entry(models.ConfigEntry.GUI_CSS_FILE)
#                if not config_entry:
#                    config_entry = models.ConfigEntry(config_key=models.ConfigEntry.GUI_CSS_FILE)
#                config_entry.config_val=form.cleaned_data['css_file'].name
#                config_entry.save()
#
#            return http.HttpResponse("""{"status": "OK"}""")
#        
        else:
            #TODO handle errors
            return http.HttpResponse("{\"status\": \"ERROR\", \"message\": \"TODO.\"}")
    else:
        form = forms.GuiSettingsForm(initial=get_initial_form_values(GUI_SETTINGS_ENTRY_MAP))
        return direct_to_template(request, 'administration/gui_settings.html', {
            'form': form,
            'css_file_name': models.get_entry_val(ConfigEntry.GUI_CSS_FILE) or settings.DEFAULT_CSS_FILE_NAME,
            'css_file_url': settings.CSS_TEMPLATES_URL +'/'+ settings.CUSTOM_CSS_FILE_NAME,
            
            'application_icons_name': models.get_entry_val(ConfigEntry.GUI_APPLICATION_ICONS) or settings.DEFAULT_APPLICATION_ICONS_NAME,
            'application_icons_url': settings.CSS_TEMPLATES_URL +'/'+ settings.CUSTOM_APPLICATION_ICONS_NAME,
            
            'filetype_icons_name': models.get_entry_val(ConfigEntry.GUI_FILETYPE_ICONS) or settings.DEFAULT_FILETYPE_ICONS_NAME,
            'filetype_icons_url': settings.CSS_TEMPLATES_URL +'/'+ settings.CUSTOM_FILETYPE_ICONS_NAME,
            
            'progress_icons_name': models.get_entry_val(ConfigEntry.GUI_PROGRESS_ICONS) or settings.DEFAULT_PROGRESS_ICONS_NAME,
            'progress_icons_url': settings.CSS_TEMPLATES_URL +'/'+ settings.CUSTOM_PROGRESS_ICONS_NAME,
            
            'main_menu_bar_name': models.get_entry_val(ConfigEntry.GUI_MAIN_MENU_BAR) or settings.DEFAULT_MAIN_MENU_BAR_NAME,
            'main_menu_bar_url': settings.CSS_TEMPLATES_URL +'/'+ settings.CUSTOM_MAIN_MENU_BAR_NAME
        
        })

def _save_settings(form, entry_map):
    for key, value in entry_map.items():
        config_object = models.get_entry(value)
        if not config_object:
            config_object = models.ConfigEntry(config_key=value)
        config_object.config_val = str(form.cleaned_data[key]).strip()
        config_object.save()

@decorators.is_superadmin
def ldap_settings(request):

    if request.method == 'POST':

        form = forms.LDAPSettingsForm(request.POST)

        if form.is_valid():
            use_ldap = models.get_entry(LDAP_SETTINGS_ENTRY_MAP['use_ldap'])
            if not use_ldap:
                use_ldap = models.ConfigEntry(config_key=models.ConfigEntry.AUTH_LDAP_IS_USED)
            use_ldap.config_val = form.cleaned_data['use_ldap']
            use_ldap.save()

            if use_ldap.config_val:
                _save_settings(form, LDAP_SETTINGS_ENTRY_MAP)

            return bls_django.HttpResponseCreated()

    else:
        form = forms.LDAPSettingsForm(initial=get_initial_form_values(LDAP_SETTINGS_ENTRY_MAP))

    groups = models.LDAPGroupConfig.objects.all()

    return direct_to_template(request, 'administration/ldap_settings.html', {
            'form': form,
            'groups': groups,
            'groupForm': forms.GroupForm()
        })

@decorators.is_superadmin
def ldap_groups(request):

    if request.method == 'GET':

        return direct_to_template(request, 'administration/ldap_groups.html', {
            'groups': models.LDAPGroupConfig.objects.all(),
        })
    elif request.method == 'POST':
        
        try:
            data = json.loads(request.raw_post_data)
        except (TypeError, ValueError):
            return http.HttpResponseBadRequest('Missing JSON body in request')

        valid, msg = validate_groups_request(data)
        if not valid:

            response = {'status':'ERROR',
                        'message': msg}
            return bls_django.HttpJsonResponse(response)

        try:
            action = data['action']
        except KeyError:
            action = ''
        if action=='add':
            response = add_action(data=data)
        elif action=='delete':
            response = delete_action(data=data)
        elif action=='edit':
            response = edit_action(data=data)
        elif action=='synchronize':
            response = synchronize_action(data=data)
        else:
            response = {'status':'ERROR',
                        'message': 'Unrecognized action'}

        return bls_django.HttpJsonResponse(response)

    else:
        return http.HttpResponseBadRequest('Unsupported HTTP method.')

    
def add_action(data):
    group_name = data['data']['group_name']
    group_dn = data['data']['group_dn']
    response = {}
    group_config = None
    is_valid_dn = validate_dn_format(group_dn)
    
    if is_valid_dn:

        group_dn = dn2str(str2dn(group_dn))

        try:
            group_config = models.LDAPGroupConfig.objects.get(group_dn=group_dn)
        except models.LDAPGroupConfig.DoesNotExist:
            pass

        if not group_config:

            group_config = models.LDAPGroupConfig(name=group_name,
                                                  group_dn=group_dn)

            group_config.save()
            response['id'] = group_config.id
            response['status'] = 'OK'
            if check_group_name_existence(group_name):
                response['message'] = GROUP_EXISTS_MESSAGE%(group_name, group_dn)
            else:
                auth_models.Group(name=group_name).save()

        else:
            response['status']='ERROR'
            response['message'] = 'LDAP group already mapped'
    else:
        response['status']='ERROR'
        response['message'] = 'Invalid DN format'

    return response

def delete_action(data):
    id = data['data']['id']
    group_config = None

    response = {}
    try:
        group_config = models.LDAPGroupConfig.objects.get(pk=id)
        group_config.delete()
        response['status']='OK'
    except models.LDAPGroupConfig.DoesNotExist:
        response['status']='ERROR'
        response['message']='Object does not exist'
    return response

def edit_action(data):
    conf_id = data['data']['id']
    group_name = data['data']['group_name']
    group_dn = data['data']['group_dn']
    response = {}
    group_config = None
    group_config_val = None
    is_valid_dn = validate_dn_format(group_dn)

    if is_valid_dn:

        group_dn = dn2str(str2dn(group_dn))

        try:
            group_config = models.LDAPGroupConfig.objects.get(pk=conf_id)
        except models.LDAPGroupConfig.DoesNotExist:
            response['status']='ERROR'
            response['message']='Object does not exist'
            return response

        try:
            group_config_val = models.LDAPGroupConfig.objects.get(group_dn=group_dn)
        except models.LDAPGroupConfig.DoesNotExist:
            pass

        if not group_config_val or group_config_val.id == int(conf_id):
            group_config.name=group_name
            group_config.group_dn=group_dn
            group_config.save()
            response['status'] = 'OK'

            if check_group_name_existence(group_name):
                response['message'] = GROUP_EXISTS_MESSAGE%(group_name, group_dn)
            else:
                auth_models.Group(name=group_name).save()

        else:
            response['status']='ERROR'
            response['message'] = 'Group DN already mapped.'
    else:
        response['status']='ERROR'
        response['message'] = 'Invalid DN format'

    return response

@transaction.commit_manually
def synchronize_action(data):
    
    try:
        conf_id = data['data']['id']
        group_config = models.LDAPGroupConfig.objects.get(pk=conf_id)
        group = auth_models.Group.objects.get(name=group_config.name)

        LDAPSynchronizer().synchronize_group(group_config.group_dn, group_config.name)
    except LDAPSynchError, e:
        transaction.rollback()
        return {'status': 'ERROR',
                'message': e.get_error_msg()}
    finally:
        transaction.commit()
        return {'status': 'OK'}



def validate_groups_request(data):
    try:
        if 'action' not in data:
            return False, 'Missing action parameter in request'
        if data['action'] not in ('delete', 'synchronize'):
            if not data['data']['group_name']:
                return False, 'Missing value for group name'
            if not data['data']['group_dn']:
                return False, 'Missing value for group dn'
    except KeyError, e:
        return False, 'General validation error, mismatched JSON content'
        
    return True, None

@decorators.is_superadmin
def reports_list(request):
    
    reports = report_models.Report.objects.filter(is_template=True, is_deleted=False)
    data = {}
    
    for report in reports: 
        data[report.id] = {
            'id': report.id,
            'name': report.name,
            'template_path': report.template_path,
            'template_url': settings.REPORTS_TEMPLATES_URL + '/' + report.template_path,
            'created_on': report.created_on.strftime('%Y-%m-%d %H:%M'),
            'modified_on': report.modified_on.strftime('%Y-%m-%d %H:%M'),
            'executed_on': 'Never',
            'note': report.note,
            'schedule_type': unicode(report_models.Report.SCHEDULE_TYPES[report.schedule_type]),
            'schedule_type_raw': report.schedule_type,
            'schedule_day': str(report.schedule_day),
            'author': ('%s %s') % (report.owner.first_name, report.owner.last_name),
            'user_required': report.user_required,
            'group_required': report.group_required,
            'course_required': report.course_required,
            'admin_required': report.admin_required,
            'user_shown': report.user_shown,
            'group_shown': report.group_shown,
            'course_shown': report.course_shown,
            'admin_shown': report.admin_shown,
            'date_from_shown': report.date_from_shown,
            'date_to_shown': report.date_to_shown,
            'results': {}
        }
    
    return bls_django.HttpJsonResponse(data)

@decorators.is_superadmin
def reports(request):
    return direct_to_template(request, 'administration/reports.html')

@decorators.is_superadmin
def reports_create(request, id=None):
    if id:
        report = get_object_or_404(report_models.Report, pk=id)
        initial = {
            'report_id': report.id,
            'name': report.name,
            'template': report.template_path,
            'user_required': report.user_required,
            'group_required': report.group_required,
            'course_required': report.course_required,
            'admin_required': report.admin_required,
            
            'user_shown': report.user_shown,
            'group_shown': report.group_shown,
            'course_shown': report.course_shown,
            'admin_shown': report.admin_shown,
            
            'date_from_shown': report.date_from_shown,
            'date_to_shown': report.date_to_shown,
            'note': report.note
        }        
    
    if request.method == 'POST':
        form = forms.ReportImportForm(request.POST, request.FILES)
        
        if form.is_valid():            
            old_template_path = None
            if form.cleaned_data['report_id']:
                report = get_object_or_404(report_models.Report, pk=form.cleaned_data['report_id'])
                old_template_path = report.template_path
            else:
                report = report_models.Report(owner=request.user)
                
            report.name = form.cleaned_data['name']
            report.user_required = form.cleaned_data['user_required']
            report.group_required = form.cleaned_data['group_required']
            report.course_required = form.cleaned_data['course_required']
            report.admin_required = form.cleaned_data['admin_required']
            
            report.user_shown = form.cleaned_data['user_shown']
            report.group_shown = form.cleaned_data['group_shown']
            report.course_shown = form.cleaned_data['course_shown']
            report.admin_shown = form.cleaned_data['admin_shown']
            
            report.date_from_shown = form.cleaned_data['date_from_shown']
            report.date_to_shown = form.cleaned_data['date_to_shown']
            report.note = form.cleaned_data['note']
            report.is_deleted = False
            
            if report.template_path and form.cleaned_data['template']:
                old_path = os.path.join(settings.REPORTS_TEMPLATES_DIR, report.template_path)
                if os.path.isfile(old_path):
                    os.remove(old_path)

            if form.cleaned_data['template']:
                template_name = report.clean_template_name(form.cleaned_data['template'].name);   
                path = os.path.join(settings.REPORTS_TEMPLATES_DIR, template_name)
                          
                with closing(storage.default_storage.open(path, 'wb')) as fh:
                    for chunk in form.cleaned_data['template'].chunks():
                        fh.write(chunk)
                        
                report.template_path = template_name

            report.use_webservice = report.uses_webservice()

            report.is_template = True
            report.save()

            if old_template_path:
                report_models.Report.objects.filter(template_path=old_template_path).update(template_path=report.template_path)
            ''' in order for ajax file upload to work properly,
                this response needs to be sent as plaintext and
                parsed to json format on the client side
            '''
            return http.HttpResponse("{\"status\": \"OK\"}")
            
        else:
            ctx = {
                   'form' : form
            }
            return direct_to_template(request, 'administration/reports_import.html', ctx)

    if id:
        form = forms.ReportImportForm(initial=initial)
        ctx = {
            'form' : form,
            'report': report
        }
    else:
        form = forms.ReportImportForm
        ctx = {
            'form' : form
        }
    return direct_to_template(request, 'administration/reports_import.html', ctx)

@decorators.is_superadmin
def reports_delete(request, id):
    report = get_object_or_404(report_models.Report, pk=id)
    if report.is_template:
        reports = Report.objects.filter(template_path=report.template_path, is_template=False).update(is_deleted=True)
        report.is_deleted = True
        report.save()
        
    return bls_django.HttpJsonOkResponse()
