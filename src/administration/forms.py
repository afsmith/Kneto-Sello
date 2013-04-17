# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 BLStream Sp. z o.o. (http://blstream.com/)
#
# Authors:
#     Marek Mackiewicz <marek.mackiewicz@blstream.com>
#

""" Forms used by application management.
"""
import os

import re

from django import forms
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.template.defaultfilters import default
from django.utils.translation import ugettext_lazy as _

from administration import models


class LDAPSettingsForm(forms.Form):
    """Form for editing LDAP settings.
    """

    MISSING_VALUE_ERROR = 'Form field %s is required'

    use_ldap = forms.BooleanField(label=_('Use LDAP'), required=False)
    ldap_url = forms.CharField(label=_('LDAP URL'), max_length=255, required=False)
    users_dn = forms.CharField(label=_('Users DN'), max_length=255, required=False)
    groups_dn = forms.CharField(label=_('Groups DN'), max_length=255, required=False)
    group_type = forms.ChoiceField(label=_('Group type'), choices=models.ConfigEntry.GROUPS_TYPES, required=False)
    user_discriminant = forms.CharField(label=_('User distinguisher'), max_length=10, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=20, required=False)
    last_name = forms.CharField(label=_('Last name'), max_length=20, required=False)
    email = forms.CharField(label=_('Email'), max_length=20, required=False)
    phone = forms.CharField(label=_('Phone'), max_length=20, required=False)


    def clean(self):
        cleaned_data = self.cleaned_data
        use_ldap = cleaned_data.get("use_ldap")

        if use_ldap:
            if not cleaned_data.get('ldap_url').strip():
                raise forms.ValidationError(self.MISSING_VALUE_ERROR%'ldap_url')
            if not cleaned_data.get('users_dn').strip():
                raise forms.ValidationError(self.MISSING_VALUE_ERROR%'users_dn')
            if not cleaned_data.get('groups_dn').strip():
                raise forms.ValidationError(self.MISSING_VALUE_ERROR%'groups_dn')
            if not cleaned_data.get('user_discriminant').strip():
                raise forms.ValidationError(self.MISSING_VALUE_ERROR%'user_discriminant')
            if not cleaned_data.get('first_name').strip():
                raise forms.ValidationError(self.MISSING_VALUE_ERROR%'first_name')
            if not cleaned_data.get('last_name').strip():
                raise forms.ValidationError(self.MISSING_VALUE_ERROR%'last_name')
            if not cleaned_data.get('email').strip():
                raise forms.ValidationError(self.MISSING_VALUE_ERROR%'email')

        # Always return the full collection of cleaned data.
        return cleaned_data


class GroupForm(forms.Form):
    '''Form for creating mapping between LDAP group and application group'''

    group_id = forms.CharField(max_length=200, widget=forms.HiddenInput, required=False)
    group_name = forms.CharField(max_length=255, required=True)
    group_dn = forms.CharField(max_length=255, required=True)

class ContentSettingsForm(forms.Form):

    UNIX_PATH_REGEX = r"^(/[a-zA-Z0-9_-]+)+/?$"
    MISSING_VALUE_ERROR = 'Form field %s is required'

    quality_of_content = forms.ChoiceField(label=_('Quality of video content'), choices=models.ConfigEntry.QUALITY_TYPES)
    use_dms = forms.BooleanField(label=_("Use DMS"), initial=False, required=False)
    dms_path = forms.CharField(label=_("DMS path"), max_length=255, required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('quality_of_content'):
            raise forms.ValidationError(self.MISSING_VALUE_ERROR % 'quality_of_content')
        if cleaned_data.get('use_dms'):
            if not cleaned_data.get('dms_path'):
                raise forms.ValidationError(_("Form field dms_path is required"))
            if not re.match(self.UNIX_PATH_REGEX, cleaned_data['dms_path']):
                raise forms.ValidationError(_("Dms path is not valid UNIX path"))
            if not os.path.isdir(cleaned_data['dms_path']):
                raise forms.ValidationError("Dms path is not directory")
        return cleaned_data

def _get_translated_available_languages():
    return [(lc, _(x)) for lc, x in settings.AVAILABLE_LANGUAGES]

class GuiSettingsForm(forms.Form):
    default_language = forms.ChoiceField(label=_("Default language"), choices=_get_translated_available_languages(), initial='en')
    custom_web_title = forms.CharField(label=_("Custom web title"), max_length=25)
    footer = forms.CharField(label=_("Footer"), max_length=70)
    logo_file = forms.FileField(label=_("Logo file"),
        widget=forms.FileInput(attrs={'id': 'logo_file', 'class': 'file', 'style':"display: none;"}),
            required=False, help_text='Required dimensions: 200x50px, format: .jpg, .png'
    )
    bg_file = forms.FileField(label=_("Background file"),
        widget=forms.FileInput(
            attrs={'id': 'bg_file', 'class': 'file', 'style': "display: none;"}),
        required=False, help_text='Required dimensions: 1024x768px, '
                                  'format: .jpg, .png'
    )
    use_logo_as_title = forms.BooleanField(label=_("Use Logo as title"),
        initial=False, required=False)
    use_bg_image = forms.BooleanField(label=_("Use background image"),
        initial=False, required=False)
    css_file = forms.FileField(label=_("Css file"), widget=forms.FileInput(attrs={'id': 'css_file', 'class': 'file', 'style': "display: none;"}), required=False)

    application_icons = forms.FileField(label=_("Application icons"), widget=forms.FileInput(attrs={'id': 'application_icons', 'class': 'file', 'style': "display: none;"}), required=False)
    filetype_icons = forms.FileField(label=_("Filetype icons"), widget=forms.FileInput(attrs={'id': 'filetype_icons', 'class': 'file', 'style': "display: none;"}), required=False)
    progress_icons = forms.FileField(label=_("Progress icons"), widget=forms.FileInput(attrs={'id': 'progress_icons', 'class': 'file', 'style': "display: none;"}), required=False)
    main_menu_bar = forms.FileField(label=_("Main menu bar"), widget=forms.FileInput(attrs={'id': 'main_menu_bar', 'class': 'file', 'style': "display: none;"}), required=False)


class SelfRegisterForm(forms.Form):
    token = forms.CharField(label=_("Token"), max_length=100)


class ReportImportForm(forms.Form):

    report_id = forms.CharField(max_length=200, widget=forms.HiddenInput, required=False)
    name = forms.CharField(label=_('Name'), max_length=50)
    template = forms.FileField(label=_('Template'), required=False)

    user_required = forms.BooleanField(label=_('Receiver required'), required=False)
    group_required = forms.BooleanField(label=_('Group required'), required=False)
    course_required = forms.BooleanField(label=_('Content required'), required=False)
    admin_required = forms.BooleanField(label=_('Sender required'), required=False)

    user_shown = forms.BooleanField(label=_('Receiver visible'), required=False)
    group_shown = forms.BooleanField(label=_('Group visible'), required=False)
    course_shown = forms.BooleanField(label=_('Content visible'), required=False)
    admin_shown = forms.BooleanField(label=_('Sender visible'), required=False)

    date_from_shown = forms.BooleanField(label=_('Date from visible'), required=False)
    date_to_shown = forms.BooleanField(label=_('Date to visible'), required=False)

    note = forms.CharField(label=_('Note'), widget=forms.Textarea(attrs={'rows': 5, 'cols': 25}), required=False)

    def __init__(self, *args, **kwargs):
        super(ReportImportForm, self).__init__(*args, **kwargs)

    def clean(self):

        cd = self.cleaned_data

        if not cd['report_id'] and not cd['template']:
            self._errors['template'] = self.error_class([_('This field is required.')])
            raise forms.ValidationError(_("Please fill up all necessary fields"))
        return cd

    def clean_name(self):
        name = self.cleaned_data['name']
        schar = '[\\,\/,\?,\|,\,,\$,\%,\&]'
        invalid_characters = re.findall(schar, name)
        if invalid_characters:
            raise forms.ValidationError(_("Report name can\'t contain special characters: %s" % (schar,)))
        return self.cleaned_data['name'].strip()


# vim: set et sw=4 ts=4 sts=4 tw=78:
