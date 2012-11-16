from __future__ import absolute_import
import os, datetime
from django import http
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from content.course_states import ActiveAssign, Active, ActiveInUse
from content.models import Course

from bls_common import bls_django
from reports import models, forms, tasks
from plato_common import decorators
from management import models as mgmnt_models

@decorators.is_admin_or_superadmin
def reports(request):
    return direct_to_template(request, 'reports/reports.html')

@decorators.is_admin_or_superadmin
def reports_create(request, id=None):

    if id:
        report = get_object_or_404(models.Report, pk=id)
        template_report = models.Report.objects.get(template_path=report.template_path, is_template=True)
        date_from = date_to = None
        if report.date_from:
            date_from = report.date_from.strftime('%Y-%m-%d')
        if report.date_to:
            date_to = report.date_to.strftime('%Y-%m-%d')
        initial = {
            'report_id': report.id,
            'name': report.name,
            'template': report.template_path,
            'note': report.note,
            'schedule_type': report.schedule_type,
            'schedule_day': 0,
            'user': report.user,
            'group': report.group,
            'course': report.course,
            'admin':  report.admin,
            'template_report': template_report.id,
            'schedule_hour': report.schedule_hour,
            'show_all': report.show_all,
            'datepicker_from': date_from,
            'datepicker_to': date_to,
        }        
        
        if report.schedule_type == models.Report.SCHEDULE_WEEKLY:
            initial['schedule_day_week'] = report.schedule_day
        elif report.schedule_type == models.Report.SCHEDULE_MONTHLY:
            initial['schedule_day_month'] = report.schedule_day

    if request.method == 'POST':
        form = forms.CreateReportForm(request.user, request.POST)

        if form.is_valid():
            if form.cleaned_data['report_id']:
                report = get_object_or_404(models.Report, pk=form.cleaned_data['report_id'])
            else:
                report = models.Report(owner=request.user)

            if request.user.get_profile().is_superadmin:
                superadmin_form = forms.SuperadminCreateReportForm(request.POST)
                superadmin_form.full_clean()
                report.show_all = superadmin_form.cleaned_data["show_all"]

            report.name = form.cleaned_data['name']
            report.note = form.cleaned_data['note']
            report.user = form.cleaned_data['user']
            report.group = form.cleaned_data['group']
            report.course = form.cleaned_data['course']
            report.admin = form.cleaned_data['admin']
            report.template_path = form.cleaned_data['template_report'].template_path
            report.schedule_hour = form.cleaned_data['schedule_hour']
            report.is_deleted = False
            report.use_webservice = form.cleaned_data['template_report'].use_webservice

            report.date_from = None
            if form.cleaned_data['datepicker_from']:
                report.date_from = datetime.datetime.strptime(form.cleaned_data['datepicker_from'], "%Y-%m-%d")

            report.date_to = None
            if form.cleaned_data['datepicker_to']:
                report.date_to =  datetime.datetime.strptime(form.cleaned_data['datepicker_to'], "%Y-%m-%d")

            report.schedule_type = form.cleaned_data['schedule_type']
            if int(form.cleaned_data['schedule_day_week']):
                report.schedule_day = int(form.cleaned_data['schedule_day_week'])
            else:
                report.schedule_day = int(form.cleaned_data['schedule_day_month'])

            template = form.cleaned_data['template_report']
            if not template.user_shown:
                report.user = None
            if not template.group_shown:
                report.group = None
            if not template.course_shown:
                report.course = None
            if not template.admin_shown:
                report.admin = None

            report.save()


            ''' in order for ajax file upload to work properly,
                this response needs to be sent as plaintext and
                parsed to json format on the client side
            '''
            return http.HttpResponse("{\"status\": \"OK\"}")

        else:
            form.fields['group'].queryset = request.user.groups
            form.fields['user'].queryset = User.objects.filter(Q(groups__in=request.user.groups.all()) &
                                                               Q(userprofile__role=mgmnt_models.UserProfile.ROLE_USER) &
                                                               Q(is_active=True)).distinct()
            form.fields['course'].queryset = Course.objects.filter(coursegroup__group__in=request.user.groups.all(),
                                                                   state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()
            form.fields['admin'].queryset = User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_ADMIN) | Q(userprofile__role=mgmnt_models.UserProfile.ROLE_SUPERADMIN) & Q(groups__in=request.user.groups.all())).distinct()

            ctx = {
                   'form' : form,
                   'superadmin_form': forms.SuperadminCreateReportForm()
            }
            return direct_to_template(request, 'reports/create.html', ctx)

    if id:
        form = forms.CreateReportForm(request.user, initial=initial)
        superadmin_form = forms.SuperadminCreateReportForm(initial=initial)
        ctx = {
            'form' : form,
            'report': report,
            'superadmin_form': superadmin_form
        }
    else:
        form = forms.CreateReportForm(request.user)
        superadmin_form = forms.SuperadminCreateReportForm()
        ctx = {
            'form' : form,
            'superadmin_form': superadmin_form
        }

    ctx['form'].fields['group'].queryset = request.user.groups
    ctx['form'].fields['user'].queryset = User.objects.filter(Q(groups__in=request.user.groups.all()) & Q(userprofile__role=mgmnt_models.UserProfile.ROLE_USER)).distinct()
    ctx['form'].fields['course'].queryset = Course.objects.filter(coursegroup__group__in=request.user.groups.all(),
                                                                  state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()
    ctx['form'].fields['admin'].queryset = User.objects.filter(Q(userprofile__role=mgmnt_models.UserProfile.ROLE_ADMIN) | Q(userprofile__role=mgmnt_models.UserProfile.ROLE_SUPERADMIN) & Q(groups__in=request.user.groups.all())).distinct()

    if 'report' in ctx and request.user.get_profile().is_superadmin and ctx['report'].show_all:
        _switch_query_sets(form.fields['user'], superadmin_form.fields['all_users'])
        _switch_query_sets(form.fields['group'], superadmin_form.fields['all_groups'])
        _switch_query_sets(form.fields['course'], superadmin_form.fields['all_courses'])
        _switch_query_sets(form.fields['admin'], superadmin_form.fields['all_admins'])

    return direct_to_template(request, 'reports/create.html', ctx)

def _switch_query_sets(form_field, superadmin_form_field):
    temp_query_set = form_field.queryset
    form_field.queryset = superadmin_form_field.queryset
    superadmin_form_field.queryset = temp_query_set

@decorators.is_admin_or_superadmin
def reports_delete(request, id):
    report = get_object_or_404(models.Report, pk=id)
    results = models.ReportResult.objects.filter(report=report.id)
    for result in results:
        path = os.path.join(settings.REPORTS_RESULTS_DIR, result.file_path)
        if os.path.isfile(path):
            os.remove(path)
    report.delete()
    return bls_django.HttpJsonOkResponse()

@decorators.is_admin_or_superadmin
def reports_list(request):

    reports = models.Report.objects.filter(owner=request.user.id, is_template=False)
    data = {}

    for report in reports:
        data[report.id] = {
            'id': report.id,
            'name': report.name,
            'owner_id': report.owner.id,
            'template_path': report.template_path,
            'template_url': settings.REPORTS_TEMPLATES_URL + '/' + report.template_path,
            'created_on': report.created_on.strftime('%Y-%m-%d %H:%M'),
            'modified_on': report.modified_on.strftime('%Y-%m-%d %H:%M'),
            'executed_on': 'Never',
            'note': report.note,
            'schedule_type': unicode(models.Report.SCHEDULE_TYPES[report.schedule_type]),
            'schedule_type_raw': report.schedule_type,
            'schedule_day': str(report.schedule_day),
            'is_deleted': report.is_deleted,
            'results': {}
        }

        results = models.ReportResult.objects.filter(report=report.id)
        for result in results:
            data[report.id]['results'][result.id] = {
                'id': result.id,
                'result_path': result.file_path[:-4],
                'result_url': settings.REPORTS_RESULTS_URL + '/' + result.file_path,
                'html_result_url': settings.REPORTS_RESULTS_URL + '/' + result.html_file_path,
                'created_on': result.created_on.strftime('%Y-%m-%d %H:%M'),
                'status': result.status
            }

        if report.executed_on:
            data[report.id]['executed_on'] = report.executed_on.strftime('%Y-%m-%d %H:%M')
        if report.schedule_type == models.Report.SCHEDULE_MONTHLY:
            data[report.id]['schedule_day'] += 'th'
        if report.schedule_type == models.Report.SCHEDULE_WEEKLY:
            data[report.id]['schedule_day'] = unicode(forms.CreateReportForm.DAYS[report.schedule_day][1])

    return bls_django.HttpJsonResponse(data)

@decorators.is_admin_or_superadmin
def get_details(request, id=None):
    report = models.Report()
    if id:
        try:
            report = get_object_or_404(models.Report, pk=id, is_template=True, is_deleted=False)
        except models.Report.DoesNotExist:
            pass

    data = {
            'user_required' : report.user_required,
            'group_required' : report.group_required,
            'course_required' : report.course_required,
            'admin_required' : report.admin_required,
            'user_shown' : report.user_shown,
            'group_shown' : report.group_shown,
            'course_shown' : report.course_shown,
            'admin_shown' : report.admin_shown,
            'date_from_shown' : report.date_from_shown,
            'date_to_shown' : report.date_to_shown,
    }
    return bls_django.HttpJsonResponse(data)

@decorators.is_admin_or_superadmin
def generate(request, id):
    tasks.generate_report.delay(id)
    return bls_django.HttpJsonResponse({'status': 'OK'})
