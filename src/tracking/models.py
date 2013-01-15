
from django.contrib.auth import models as auth_models
from django.db import models
from django import http
from content.course_states import Active, ActiveAssign, ActiveInUse
from content.models import Segment, Course
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

class TrackingEvent(models.Model):

    START_EVENT_TYPE = "START"
    END_EVENT_TYPE = "END"

    segment = models.ForeignKey(Segment)
    participant = models.ForeignKey(auth_models.User)
    created_on = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(_('event type'), max_length=50)
    is_scorm = models.BooleanField(_('is scorm'), default=False)
    score_min = models.FloatField(_('scorm min score'), null=True)
    score_raw = models.FloatField(_('scorm raw score'), null=True)
    score_max = models.FloatField(_('scorm max score'), null=True)
    lesson_status = models.CharField(_('lesson status'), max_length=50, null=True)
    parent_event = models.ForeignKey('self', null=True)
    scorm_status = models.CharField(_('scorm status'), max_length=50, null=True)

    class Meta:
        ordering = ('created_on',)

class TrackingEventService(object):
    
    def segments(self, user_id, course_id):
        learnt_segments = Segment.objects.filter(track=0,
                                                   course=course_id,
                                                   course__groups__user=user_id,
                                                   trackingevent__event_type=TrackingEvent.END_EVENT_TYPE,
                                                   trackingevent__lesson_status='completed',
                                                   trackingevent__participant=user_id)
        result = []
        for segment in Segment.objects.filter(track=0, course=course_id, course__groups__user=user_id).distinct():
            segment.is_learnt = len(learnt_segments.filter(id=segment.id)) > 0
            segment.available = True
            result.append(segment)
        return result
    
    def segmentIsLearnt(self, user_id, segment_id):
        segment = Segment.objects.filter(track=0,
                                           id=segment_id,
                                           course__groups__user=user_id,
                                           trackingevent__event_type=TrackingEvent.END_EVENT_TYPE,
                                           trackingevent__lesson_status='completed',
                                           trackingevent__participant=user_id)
        return len(segment) > 0

    def trackingHistory(self, segment_id, participant_id, date_from=datetime.min, date_to=datetime.max):
        events = TrackingEvent.objects.filter(segment__id=segment_id, participant=participant_id)
        tracking_list = []
        start_date = None
        for event in events:
            if event.event_type == TrackingEvent.START_EVENT_TYPE:
                start_date = event.created_on
            elif event.event_type == TrackingEvent.END_EVENT_TYPE:
                end_date = event.created_on

                if start_date != None:
                    delta = end_date - start_date
    
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
    
                    tracking_element = {
                        'id': event.id,
                        'date':start_date,
                        'duration': '%02d:%02d:%02d'%(hours,minutes,seconds),
                        'result': None,
                        }
                    if event.is_scorm:
                        tracking_element['result'] = '(%d/%d/%d) %s'%(event.score_min if event.score_min else 0,
                                                                      event.score_raw if event.score_raw else 0,
                                                                      event.score_max if event.score_max else 0,
                                                                      event.scorm_status if event.scorm_status else '')
                    if ((seconds > 0 or minutes > 0 or hours > 0) or \
                        (event.score_min or event.score_raw or event.score_max or event.lesson_status)) and (date_from <= start_date <= date_to):   
                        tracking_list.append(tracking_element)
        return tracking_list


def segments_count(courses_with_learnt_segments, course_id):
    for course in courses_with_learnt_segments:
        if course.id == course_id:
            return course.segments_count
    return 0

def active_modules_with_track_ratio_sorted_by_last_event(user_id):
    courses_with_all_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct segment.id) as segments_count,
        (SELECT max(created_on) FROM tracking_trackingevent as tte, content_segment as cs WHERE tte.segment_id = cs.id
        AND tte.event_type = 'END' AND tte.participant_id=%d AND cs.course_id=course_group.course_id AND tte.lesson_status = 'completed') as last_learn_date
        from content_coursegroup course_group
        join content_course course on course_group.course_id = course.id
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        and track = 0
        where user_group.user_id = %d
        and course.state_code in (2, 3, 4)
        group by course_group.course_id
        order by last_learn_date DESC""" % (int(user_id), int(user_id)))

    courses_with_learnt_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct trackingevent.segment_id) as segments_count
        from content_coursegroup course_group
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        left join tracking_trackingevent trackingevent on trackingevent.segment_id = segment.id
            and trackingevent.event_type = 'END'
            and trackingevent.lesson_status = 'completed'
            and trackingevent.participant_id = %d
        where user_group.user_id = %d
        and track = 0
        group by course_group.course_id""" % (int(user_id), int(user_id)))

    result = []
    for course in courses_with_all_segments:
        result.append({"id": course.id,
                       "ratio":(float(segments_count(courses_with_learnt_segments, course.id)) / float(course.segments_count))})
    return result
        
def active_modules_with_track_ratio(user_id, group_id):
    courses_with_all_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct segment.id) as segments_count
        from content_coursegroup course_group
        join content_course course on course_group.course_id = course.id
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
            and track = 0
        where user_group.user_id = %d
        and auth_group.id = %d
        and course.state_code in (2, 3, 4)
        group by course_group.course_id""" % (int(user_id), int(group_id)))

    courses_with_learnt_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct trackingevent.segment_id) as segments_count
        from content_coursegroup course_group
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        left join tracking_trackingevent trackingevent on trackingevent.segment_id = segment.id
            and trackingevent.event_type = 'END'
            and trackingevent.lesson_status = 'completed'
            and trackingevent.participant_id = %d
        where user_group.user_id = %d
        and auth_group.id = %d
        and track = 0
        group by course_group.course_id""" % (int(user_id), int(user_id), int(group_id)))

    result = []
    for course in courses_with_all_segments:
        result.append({"id": course.id,
                       "ratio":(float(segments_count(courses_with_learnt_segments, course.id)) / float(course.segments_count))})

    return result

def module_with_track_ratio(user_id, course_id):
    course = Course.objects.get(id=course_id)
    segment_count = Segment.objects.filter(course=course_id, track=0).count()
    course_with_learnt_segments = Course.objects.raw("""
        select course_group.course_id as id, count(distinct trackingevent.segment_id) as segments_count
        from content_coursegroup course_group
        join auth_group auth_group on auth_group.id = course_group.group_id
        join auth_user_groups user_group on user_group.group_id = course_group.group_id
        join content_segment segment on segment.course_id = course_group.course_id
        left join tracking_trackingevent trackingevent on trackingevent.segment_id = segment.id
            and trackingevent.event_type = 'END'
            and trackingevent.lesson_status = 'completed'
            and trackingevent.participant_id = %d
        where user_group.user_id = %d
        and course_group.course_id = %d
        and track = 0
        group by course_group.course_id""" % (int(user_id), int(user_id), int(course_id)))
    if segment_count > 0:
        return float(segments_count(course_with_learnt_segments, course.id)) / float(segment_count)
    else:
        return 0

class ScormActivityDetails(models.Model):

    segment = models.ForeignKey(Segment)
    user = models.ForeignKey(auth_models.User)
    tracking = models.ForeignKey(TrackingEvent)
    name = models.CharField(max_length=100)
    result = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    student_response = models.CharField(max_length=100)

    class Meta:
        ordering = ('tracking', 'tracking__created_on')