from django import forms
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
import content
from content.course_states import Active, ActiveAssign, ActiveInUse
from content.forms import UserModelChoiceField
from models import Report
from django.contrib.auth.models import User, Group
from content.models import Course
from management import models as mgmnt_models

class SuperadminCreateReportForm(forms.Form):
    all_users = content.forms.UserModelChoiceField(User.objects.filter(userprofile__role=mgmnt_models.UserProfile.ROLE_USER), empty_label='', required=False, widget=forms.Select(attrs={'style': 'display:none;'}))
    all_admins = content.forms.UserModelChoiceField(User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_ADMIN) |
                                                       Q(userprofile__role=mgmnt_models.UserProfile.ROLE_SUPERADMIN)), empty_label='', required=False, widget=forms.Select(attrs={'style': 'display:none;'}))
    all_groups = forms.ModelChoiceField(Group.objects.all(), empty_label='', required=False, widget=forms.Select(attrs={'style': 'display:none;'}))
    all_courses = forms.ModelChoiceField(Course.objects.filter(state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)), empty_label='', required=False, widget=forms.Select(attrs={'style': 'display:none;'}))

    show_all = forms.BooleanField(label=_('Show all'), widget=forms.CheckboxInput(attrs={'id': 'show_all'}), required=False)

class CreateReportForm(forms.Form):

    DAYS = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday'))
    )

    report_id = forms.CharField(max_length=200, widget=forms.HiddenInput, required=False)
    name = forms.CharField(label=_('Name'), max_length=50, required=True)

    template_report = forms.ModelChoiceField(Report.objects.filter(is_template=True, is_deleted=False), label=_('Template report'), empty_label='', required=False)

    schedule_type = forms.ChoiceField(label=_('Execution'), choices=Report.SCHEDULE_TYPES_CHOICES)
    schedule_day_month = forms.ChoiceField(label=_(' '), choices=zip(range(1,32), range(1, 32)), required=False)
    schedule_day_week = forms.ChoiceField(label=_(' '), choices=DAYS, required=False)
    schedule_hour = forms.CharField(label=_('Schedule hour'), max_length=5, required=False, initial='00:00')

    note = forms.CharField(label=_('Note'), widget=forms.Textarea(attrs={'rows': 5, 'cols': 25}), required=False)

    # These are being filtered in view
    user = content.forms.UserModelChoiceField(User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_USER)), label=_('User'), empty_label='', required=False)
    group = forms.ModelChoiceField(Group.objects.all(), label=_('Group'), empty_label='', required=False)
    course = forms.ModelChoiceField(Course.objects.all(), label=_('Course'), empty_label='', required=False)
    admin = content.forms.UserModelChoiceField(User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_ADMIN) |
                                                       Q(userprofile__role=mgmnt_models.UserProfile.ROLE_SUPERADMIN)), label=_('Admin'), empty_label='', required=False)

    datepicker_from = forms.CharField(label=_('Date from'), max_length=50, required=False, widget=forms.TextInput(attrs={'disabled': 'true'}))
    datepicker_to = forms.CharField(label=_('Date to'), max_length=50, required=False, widget=forms.TextInput(attrs={'disabled': 'true'}))

    def __init__(self, user, *args, **kwargs):
        super(CreateReportForm, self).__init__(*args, **kwargs)

    def clean(self):
        cd = self.cleaned_data

        errors_found = False
        if not 'template_report' in cd or not cd['template_report']:
            self._errors['template_report'] = self.error_class([_('This field is required.')])
            errors_found = True
        else:
            template_report = cd['template_report']
            if (template_report.user_required and (not 'user' in cd or not cd['user'])):
                self._errors['user'] = self.error_class([_('This field is required.')])
                errors_found = True

            if (template_report.group_required and (not 'group' in cd or not cd['group'])):
                self._errors['group'] = self.error_class([_('This field is required.')])
                errors_found = True

            if (template_report.course_required and (not 'course' in cd or not cd['course'])):
                self._errors['course'] = self.error_class([_('This field is required.')])
                errors_found = True

            if (template_report.admin_required and (not 'admin' in cd or not cd['admin'])):
                self._errors['admin'] = self.error_class([_('This field is required.')])
                errors_found = True

        if not 'name' in cd or not cd['name']:
            self._errors['name'] = self.error_class([_('This field is required.')])
            errors_found = True

        if errors_found:
            raise forms.ValidationError(_("Please fill up all necessary fields"))

        if cd['schedule_day_month'] == "":
            cd['schedule_day_month'] = 0

        if cd['schedule_day_week'] == "":
            cd['schedule_day_week'] = 0

        return cd
