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

from datetime import datetime
import json, StringIO, logging, urllib

from django.conf import settings
from django import http
from django.contrib.auth import models as auth_models
from django.contrib.auth import decorators as auth_decorators
from django.db import models as db_models, transaction
from django.db.models import Sum
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.views.decorators import http as http_decorators
from django.views.generic.simple import direct_to_template

from bls_common import bls_django
from content import models as cont_models, serializers
import content
from content.course_states import Active, ActiveAssign, ActiveInUse
from content.models import DownloadEvent
from management import models as manage_models
from management.models import OneClickLinkToken, UserProfile
from management.views import one_click_link
from messages_custom.models import MailTemplate
from messages_custom.utils import send_goodbye_email, send_email, send_message
from plato_common import decorators
from tracking.models import ScormActivityDetails, TrackingEventService, active_modules_with_track_ratio, module_with_track_ratio
from tracking.utils import progress_formatter
from reports import reports

logger = logging.getLogger("assignments")

"""
is_admin_or_superadmin = decorators.user_passes_test(
    lambda u: u.get_profile().role in (
        manage_models.UserProfile.ROLE_ADMIN,
        manage_models.UserProfile.ROLE_SUPERADMIN)
    )

is_user = decorators.user_passes_test(
    lambda u: u.get_profile().role == manage_models.UserProfile.ROLE_USER
    )
"""

@transaction.commit_manually
@decorators.is_admin_or_superadmin
def group_modules(request):

    """
        Handles groups-modules assignments.

        :param request: Request

        return values:
        - 200
    """

    if request.method == 'POST':

        try:
            data = json.loads(request.raw_post_data)
            assignments = data['assignments']
            add_one_click_link = data['add_one_click_link'] if 'add_one_click_link' in data else False
        except ValueError:
            response = {
                    'status': 'ERROR',
                    'messages': ['Invalid JSON content.'],
                    }
            return bls_django.HttpJsonResponse(response)

        curr_time = datetime.now()

        for group_id in assignments.keys():
            #
            # Checking if group has associations to modules which should be removed
            #
            try:
                group = auth_models.Group.objects.get(pk=group_id)
            except auth_models.Group.DoesNotExist:
                transaction.rollback()
                response = {
                    'status': 'ERROR',
                    'messages': ['Group with ID %s does not exist.' % group_id],
                    }
                return bls_django.HttpJsonResponse(response)

            for module in group.course_set.all():
                if str(module.id) not in assignments[group_id]:
                    cont_models.CourseGroup.objects.filter(course=module, group=group).delete()

                    if module.get_state().has_code(ActiveAssign.CODE) and cont_models.CourseGroup.objects.filter(course=module).count() == 0:
                        module.get_state().act('remove_assignments')

            #
            # Checking if group has any new associations to modules and saving them
            #
            for module_id in assignments[str(group.id)]:
                try:
                    module = cont_models.Course.objects.get(pk=module_id)
                except cont_models.Course.DoesNotExist:
                    transaction.rollback()
                    response = {
                        'status': 'ERROR',
                        'messages': ['Course with ID %s does not exist.' % module_id],
                        }
                    return bls_django.HttpJsonResponse(response)
                if module not in group.course_set.all():
                    course_group = cont_models.CourseGroup(group=group, course=module, assigned_on=curr_time, assigner=request.user)
                    course_group.save()

                    if module.get_state().has_code(Active.CODE):
                        module.get_state().act('assign')

                    for user in group.user_set.filter(userprofile__role=manage_models.UserProfile.ROLE_USER,
                                                      is_active=True):
                        if not user.get_profile().ldap_user and add_one_click_link:
                            OneClickLinkToken.objects.filter(user=user).delete()
                            ocl = OneClickLinkToken.objects.create(user=user)
                            send_email(recipient=user,
                                        msg_ident=MailTemplate.MSG_IDENT_ADD_ASSIGNMENT_OCL,
                                        msg_data={'[groupname]':group.name,
                                                  '[moduletitle]':module.title,
                                                  "[oneclicklink]": MailTemplate.ONE_CLICK_LINK % (request.get_host(), ocl.token)})
                        else:
                            send_email(recipient=user,
                                       msg_ident=MailTemplate.MSG_IDENT_ADD_ASSIGNMENT,
                                       msg_data={'[groupname]':group.name,
                                                 '[moduletitle]':module.title})

        transaction.commit()
        return bls_django.HttpJsonResponse({'status':'OK', 'messages': []})

    else:
        serialized_set = {}
        groups = auth_models.Group.objects.all()
        for group in groups:
            serialized_set[group.id] = {}
            for module in group.course_set.filter(Q(state_code=ActiveAssign.CODE) |
                                                  Q(state_code=ActiveInUse.CODE) |
                                                  Q(state_code=Active.CODE)):
                module_dict = serializers.serialize_course(module, request.user, TrackingEventService())['meta']
                module_dict['short_title'] = module_dict['title'][:7] + '...'
                module_dict['owner'] = ' '.join((module.owner.first_name,module.owner.last_name))
                serialized_set[group.id][module.id] = module_dict

        return bls_django.HttpJsonResponse(serialized_set)

@decorators.is_user
def user_modules(request):

    """
        Handles requests for modules assigned to groups of logged in user.

         return values:
         - 200 if request successfully fulfilled, response contains JSON object containing list of
                modules assigned to groups of specified user,
         - 302 if logged in user is not a normal user
    """
    modules = []
    finished_modules = []
    cg = {}

    for course_group in cont_models.CourseGroup.objects.filter(
        Q(group__in=request.user.groups.all()) &
        (Q(course__state_code=ActiveAssign.CODE) | Q(course__state_code=ActiveInUse.CODE))):
        value = None;
        try:
            value = cg[course_group.course]
            if value.assigned_on > course_group.assigned_on:
                cg[course_group.course] = course_group
        except KeyError, e:
            cg[course_group.course] = course_group

    result = sorted(cg.values(), key=lambda value: value.assigned_on, reverse=True)
    for course_group in result:
        course_group.course.segments_with_learnt_flag = TrackingEventService().segments(request.user.id, course_group.course.id)
        # -- a course is considered new only if it does not have any tracking history connected to working user
        course_group.course.is_new = 0
        for segment in course_group.course.segments_with_learnt_flag:
            course_group.course.is_new += len(TrackingEventService().trackingHistory(segment.id, request.user.id))
            segment.available=True
        course_group.course.is_new = not bool(course_group.course.is_new)
        course_group.course.duration = cont_models.Segment.objects.filter(course=course_group.course, track=0).aggregate(Sum('file__duration'))['file__duration__sum']
        if module_with_track_ratio(request.user.id, course_group.course.id) == 1:
            course_group.course.is_new = False
            finished_modules.append(course_group.course)
        else:
            if not course_group.course.allow_skipping:
                course_group.course.segments_with_learnt_flag = cont_models.\
                                                        get_segments_with_available_flag(course_group.course.segments_with_learnt_flag)
            modules.append(course_group.course)


    ctx = {
       'courses': modules,
       'finished_courses': finished_modules
    }

    return direct_to_template(request, "assignments/user_modules.html", ctx)


@auth_decorators.login_required
def dashboard(request):
    """
        Handles initial screen display. Called when empty context is requested.
    """
    
    if request.user.get_profile().role in (
        manage_models.UserProfile.ROLE_ADMIN,
        manage_models.UserProfile.ROLE_SUPERADMIN
    ):
        return admin_status(request)
    else:
        return user_modules(request)


@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def admin_status(request):
    """
        Handles preparing the screen for admin-status page.
        200 - if request successfully fulfilled, returned context contains:
                'groups' - list of groups (all groups for superadmin),
                'data' - data of every group (id, courses, users_data)
        405 - if request method is not GET.
    """

    groups = []

    if request.user.get_profile().role == manage_models.UserProfile.ROLE_ADMIN:
        my_groups = request.user.groups.all()
        groups = request.user.groups.all()

    elif request.user.get_profile().role == manage_models.UserProfile.ROLE_SUPERADMIN:
        my_groups = request.user.groups.all()
        groups = auth_models.Group.objects.all()


    group_data = {}
    for group in groups:
        group_data[group] = {}
        group_data[group]['id'] = group.id
        group_data[group]['courses']= group.course_set.annotate(
            segments_count=db_models.aggregates.Count("segment")).filter(
                (Q(state_code=ActiveAssign.CODE) |
                 Q(state_code=ActiveInUse.CODE)) &
                ~db_models.query_utils.Q(segments_count = 0)).reverse()
        group_data[group]['users_data'] = []
        for user in group.user_set.all():
            if user.get_profile().role == manage_models.UserProfile.ROLE_USER:
                mods = active_modules_with_track_ratio(user.id, group.id)
                if len(mods) > 0:
                    mods.reverse()
                    
                for row in mods:
                    row['ratio'] = progress_formatter(row['ratio'])
                group_data[group]['users_data'].append([user, mods])
        
        group_data[group]['users_data'].sort(lambda x,y : cmp(x[0].last_name.lower(), y[0].last_name.lower()))
        
    ctx = {
        'data': group_data,
        'groups': groups,
        'my_groups': my_groups
    }

    return direct_to_template(request, 'assignments/admin_status.html', ctx)

@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def user_progress(request):
    """
        Handles preparing the screen for user-progress page.

        :params request: Request

        200 - if request successfully fulfilled, returned context contains:
                user_obj - user whose progress is shown,
                course - course for which progress is shown,
                
        404 - if user with supplied user_id was not found or
              if course with supplied course_id was not found
        405 - if request method is not GET
    """

    user_id = request.GET.get('user_id', '')
    course_id = request.GET.get('course_id', '')

    user = get_object_or_404(auth_models.User, pk=user_id)
    course = get_object_or_404(cont_models.Course, pk=course_id)
    tracking_service = TrackingEventService()
    course_ratio = module_with_track_ratio(user_id=user.id, course_id=course.id)

    segments_tracking = tracking_service.segments(user_id=user.id, course_id=course.id)
    if not course.allow_skipping:
        segments_tracking = cont_models.get_segments_with_available_flag(segments_tracking)

    segments = {}
    for segment in segments_tracking:
        trackings = {}
        tracking_list = tracking_service.trackingHistory(segment_id=segment.id, participant_id=user.id)

        hours = 0
        minutes = 0
        seconds = 0
        for tracking in tracking_list:
            trackings[tracking['id']] = ScormActivityDetails.objects.filter(segment=segment,
                                                                    user=user,
                                                                    tracking__id=tracking['id']) or []
            hours += int(tracking['duration'].split(":")[0])
            minutes += int(tracking['duration'].split(":")[1])
            seconds += int(tracking['duration'].split(":")[2])

        segments[segment.start] = {'segment' : segment,
                                   'total_time': '%02d:%02d:%02d'%(reports.calculate_time(hours, minutes, seconds)),
                                   'download_count': DownloadEvent.objects.filter(segment=segment, user=user).count(),
                                   'trackings' : tracking_list,
                                   'results' : trackings}
    ctx = {
        'user_obj': user,
        'course': course,
        'ratio': progress_formatter(course_ratio),
        'segments': segments
    }
    
    return direct_to_template(request, 'assignments/user_progress.html', ctx)


def _users_per_module(owner_id, group_id=None, show_all=True):
    owner_groups = reports.get_owner_groups(owner_id, show_all)
    courses = cont_models.Course.objects.filter(groups__in=owner_groups.values_list('id', flat=True),
                                                state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).distinct()

    if group_id:
        courses = courses.filter(groups=group_id)

    course_users = {}
    for course in courses:
        course_users[course.id] = {"title" : course.title,
                                   "users_count" : str(auth_models.User.objects.filter(
                                       userprofile__role=UserProfile.ROLE_USER,
                                       groups__in=course.groups.values_list('id', flat=True),
                                       is_active=True).distinct().count())}

    return course_users

def users_per_module(request):
    report = reports.get_report_from_request(request)
    
    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)
    course_users = _users_per_module(report.owner_id, report.group_id, report.show_all)
    for id in course_users:
        writer.writerow([course_users[id]["title"], course_users[id]["users_count"]])
        
    return reports.get_csv('users_per_module.csv', result)

def published_modules(request):
    report = reports.get_report_from_request(request)
    owner_groups = reports.get_owner_groups(report.owner_id, report.show_all)

    if report.group_id:
        groups = auth_models.Group.objects.filter(id=report.group_id, id__in=owner_groups)
    else:
        groups = auth_models.Group.objects.filter(id__in=owner_groups)
    
    result = StringIO.StringIO()
    writer = reports.UnicodeWriter(result)

    for group in groups:
        modules_count = cont_models.Course.objects.filter(groups=group,
                                                          state_code__in=(Active.CODE, ActiveAssign.CODE, ActiveInUse.CODE)).count()
        writer.writerow([group.name, str(modules_count)])
    
    return reports.get_csv('published_modules.csv', result)