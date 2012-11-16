from datetime import datetime
import os, shutil, subprocess, tempfile, csv, cStringIO, codecs
import logging
import calendar

from django.conf import settings
from django.contrib.auth.models import User, Group
from django import http
from django.core.servers.basehttp import FileWrapper
from django.db.models.query_utils import Q

from messages_custom.models import MailTemplate
from messages_custom.utils import send_email, send_message
from models import Report, ReportResult
from tracking.models import TrackingEventService

class ReportGenerationService(object):
    """Generates all reports
    """

    def generate_reports(self):
        for report in self._get_periodic_reports(datetime.now()):
            if report.is_runnable() and not report.is_deleted:
                self._generate(report)

    def _get_periodic_reports(self, datetime):
        schedule_hour = str(datetime.hour).zfill(2) + ":" + str(datetime.minute).zfill(2)

        daily = Report.objects.filter(schedule_type=Report.SCHEDULE_DAILY, schedule_hour=schedule_hour)
        weekly = Report.objects.filter(schedule_type=Report.SCHEDULE_WEEKLY, schedule_hour=schedule_hour, schedule_day=datetime.weekday())
        monthly = Report.objects.filter(schedule_type=Report.SCHEDULE_MONTHLY, schedule_hour=schedule_hour)
        if calendar.monthrange(datetime.year, datetime.month)[1] == datetime.day:
            monthly = monthly.filter(schedule_day__gte=datetime.day)
        else:
            monthly = monthly.filter(schedule_day=datetime.day)

        return list(self._add_date_ranges_filter(daily, datetime.date())) + \
               list(self._add_date_ranges_filter(weekly, datetime.date())) + \
               list(self._add_date_ranges_filter(monthly, datetime.date()))

    def _add_date_ranges_filter(self, query, date):
        return query.filter((Q(date_from__isnull=True) | Q(date_from__lte=date)) & (Q(date_to__isnull=True) | Q(date_to__gte=date)))

    def generate_report(self, id):
        report = Report.objects.get(id=id)
        if not report.is_deleted:
            self._generate(report)

    def _generate(self, report):
        report_generator = ReportGenerator()
        now = datetime.now()
        file_name = report.name + '_' + now.strftime("%y-%m-%d %H:%M") + '_' + report.owner.username + '.pdf'
        html_file_name = report.name + '_' + now.strftime("%y-%m-%d %H:%M") + '_' + report.owner.username + '.html'

        file_path = os.path.join(settings.REPORTS_RESULTS_DIR, file_name)
        html_file_path = os.path.join(settings.REPORTS_RESULTS_DIR, html_file_name)

        status = report_generator.generate(report, file_path) & report_generator.generate(report, html_file_path)

        report.executed_on = now
        report.save()
        report_result = ReportResult(report=report, file_path='' if status else file_name, html_file_path='' if status else html_file_name, created_on=now, status=status)
        report_result.save()

        template = MailTemplate.objects.get(type=MailTemplate.TYPE_INTERNAL,
                                            identifier=MailTemplate.MSG_IDENT_REPORT_GENERATION)
        params_dict={'[reportname]':report.name}
        send_message(sender=report.owner,
                     recipients_ids=[report.owner.id],
                     subject=template.populate_params_to_text(template.subject, params_dict),
                     body=template.populate_params(params_dict))

class ReportGenerator(object):
    """Generates report file
    """

    _logger = logging.getLogger("ReportGenerator")

    def _get_command(self):
        cmd = ['java', '-jar', settings.REPORTS_ENGINE_DIR]
        return cmd

    def _run_command(self, cmd, cwd=None):
        try:
            self._logger.debug('Trying to generate report with command %s', cmd)
            p = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                close_fds=True, cwd=cwd)
            stdout, _ = p.communicate()
            print stdout
            return p.returncode
        except Exception, e:
            self._logger.error('Error generating report', e)

    def _prepare_params(self, report):
        result = []
        result.append('owner_id=%d'%report.owner_id)
        result.append('report_id=%d'%report.id)
        result.append('use_webservice=%s'%report.use_webservice)
        for param in ('user', 'group', 'course','admin'):
            value = getattr(report, param)
            if value:
                result.append('='.join((param, str(value.id))))
        for param in ('date_from', 'date_to'):
            value = getattr(report, param)
            if value:
                result.append('='.join((param, value.strftime('%Y-%m-%d'))))
        return "&".join(result)

    def generate(self, report, file_path):
        cmd = self._get_command()
        cmd.append(os.path.join(settings.REPORTS_TEMPLATES_DIR, report.template_path))
        cmd.append(file_path)
        cmd.append(self._prepare_params(report))
        if not report.use_webservice:
            cmd.append(settings.REPORTS_CONFIG)
        print " ".join(["'%s'" % k for k in cmd])
        return self._run_command(cmd)

def get_csv(filename, result):
    response = http.HttpResponse(FileWrapper(result), content_type='text/csv;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=\"%s\"" % filename.encode('utf8')
    response['Content-Length'] = result.tell()
    result.seek(0)
    return response

def calculate_time(hours, minutes, seconds):
    add_minutes, sec = divmod(seconds, 60)
    minutes += add_minutes
    add_hours, min = divmod(minutes, 60)
    hours += add_hours
    return hours, min, sec

def get_tracking(user, course, date_from, date_to):
    tracking_service = TrackingEventService()
    segments_tracking = tracking_service.segments(user_id=user.id, course_id=course.id)

    segments = {}
    for segment in segments_tracking:
        segments[segment.start] = {'segment' : segment, 'tracking' : tracking_service.trackingHistory(segment.id, user.id, date_from, date_to)}
    return segments

def get_report_owner(report_id):
    return Report.objects.get(pk=report_id).owner

def get_report_from_request(request):
    return Report.objects.get(pk=request.GET.get('report_id', ''))

def get_owner_groups(owner_id, show_all=True):
    report_owner = User.objects.get(pk=owner_id)
    if report_owner.get_profile().is_superadmin and show_all:
        owner_groups = Group.objects.all()
    else:
        owner_groups = report_owner.groups.all()
    return owner_groups

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

