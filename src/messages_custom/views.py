from datetime import datetime
import os
import json
import uuid
import re
from smtplib import SMTPConnectError, SMTPException
from messages.forms import ComposeForm
from messages.models import Message
from messages.utils import format_quote
from django.db.models import Q

from django.conf import settings
from django.contrib.auth import models as auth_models,\
        decorators as auth_decorators
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect,\
        HttpResponseBadRequest, HttpResponseNotFound,\
        HttpResponse, HttpResponseForbidden
from django.template.context import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.views.decorators import http as http_decorators
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template
from django.utils.html import strip_tags
from bls_common.bls_django import HttpJsonOkResponse, HttpJsonResponse
from forms import CustomComposeForm, TemplateForm
from models import MailTemplate, MessageProfile
from messages.models import Message
from utils import send_message, resend_message
from plato_common import decorators as plato_decorators
from content.models import Course
from management import models as manage_models



if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


@auth_decorators.login_required
def inbox(request):
    request_data = _get_request_data(request)
    course_id = request_data['course_id']

    message_list = Message.objects.inbox_for(request.user)
    if course_id:
        try:
            course = Course.objects.get(pk=course_id)
            message_list = message_list.filter(messageprofile__courses=course)
        except Course.DoesNotExist:
            pass

    response = render_to_response("messages/inbox.html", {
        'message_list': message_list,
        "modules": _get_modules(request),
        "selected_module_id": course_id,
        }, context_instance=RequestContext(request))

    return _set_response_data(request, response)


@plato_decorators.is_admin_or_superadmin
@http_decorators.require_GET
def ocl(request):
    request_data = _get_request_data(request)
    course_id = request_data['course_id']
    show_my_ocl_links = request_data['show_my_ocl_links']
    
    message_list = _get_ocl_messages(request.user, course_id,
            show_my_ocl_links)
    response = render_to_response("messages/ocl.html", {
        'message_list': message_list,
        "modules": _get_modules(request),
        "selected_module_id": course_id,
        "show_my_ocl_links": show_my_ocl_links
        }, context_instance=RequestContext(request))

    return _set_response_data(request, response)

@auth_decorators.login_required
def outbox(request):
    request_data = _get_request_data(request)
    course_id = request_data['course_id']
    ocl_only = request_data['ocl_only']
    show_my_ocl_links = request_data['show_my_ocl_links']

    if ocl_only == 'true':
        message_list = _get_ocl_messages(request.user, course_id,
                show_my_ocl_links)
    else:
        message_list = Message.objects.outbox_for(request.user)
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                message_list = message_list.filter(messageprofile__courses=course)
                course_id = int(course_id)
            except Course.DoesNotExist:
                pass

    response = render_to_response("messages/outbox.html", {
        'message_list': message_list,
        "modules": _get_modules(request),
        "selected_module_id": course_id,
        "ocl_only": ocl_only,
        }, context_instance=RequestContext(request))

    return _set_response_data(request, response)

@auth_decorators.login_required
def view(request, message_id, template_name='messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either 
    the sender or the recipient. If the user is not allowed a 404
    is raised. 
    If the user is the recipient and the message is unread 
    ``read_at`` is set to the current datetime.
    """
    ocl = request.GET.get('ocl', None)
    user = request.user
    now = datetime.now()
    message = get_object_or_404(Message, id=message_id)
    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        message.save()
    message.body = strip_tags(message.body)
    
    if ocl == 'true':
        template_name = "messages/view_ocl.html"

    return render_to_response(template_name, {
        'message': message,
    }, context_instance=RequestContext(request))


@auth_decorators.login_required
def reply(request, message_id):
    parent = get_object_or_404(Message, id=message_id)
    if request.method == "POST":
        try:
            data = json.loads(request.raw_post_data)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON content.')
        send_message(request.user, data['recipients'], data['subject'], data['body'] + "\n\n" + format_quote(parent.body), parent)
        return HttpJsonOkResponse()
    else:
        return render_to_response("messages/compose.html",
                                  {'form': CustomComposeForm({'body': _(u"%(date)s, %(sender)s wrote:\n%(body)s\n\n") %
                                                                      {'date': parent.sent_at.strftime('%Y-%m-%d %H:%M'),
                                                                       'sender': parent.sender.first_name + ' ' + parent.sender.last_name,
                                                                       'body': format_quote(parent.body)},
                                                              'subject': _(u"Re: %(subject)s") %
                                                                         {'subject': parent.subject}}),
                                   'message_id': message_id}, context_instance=RequestContext(request))


@auth_decorators.login_required
@http_decorators.require_GET
def resend(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        raise Http404

    try:
        resend_message(message)
    except Exception, e:
        return HttpJsonResponse({'status': 'ERROR', 
            'error': unicode(_('There was a problem with re-sending message: %s'\
                    ' Try again later.' % e))})

    return HttpJsonOkResponse()


@auth_decorators.login_required
def compose(request):
    if request.method == "POST":
        try:
            data = json.loads(request.raw_post_data)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON content.')
        
        courses = []
        try:
            if data.get('course_id'):
                courses.append(Course.objects.get(pk=data.get('course_id')))
        except Course.DoesNotExist:
            pass

        send_message(request.user, data['recipients'], data['subject'], data['body'], courses=courses)
        return HttpJsonOkResponse()
    else:
        return render_to_response("messages/compose.html",
                {'form': CustomComposeForm()}, context_instance=RequestContext(request))

@auth_decorators.login_required
@http_decorators.require_POST
def delete(request, message_id):
    user = request.user
    now = datetime.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
        user.message_set.create(message=_(u"Message successfully deleted."))
        if notification:
            notification.send([user], "messages_deleted", {'message': message,})
        return HttpJsonOkResponse()
    return HttpJsonResponse({'status': 'ERROR', 'error': 'Not owner.'})


@auth_decorators.login_required
@http_decorators.require_POST
def delete_multiple(request):
    user = request.user

    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON content.')

    now = datetime.now()
    for message_id in data['messages']:
        try:
            message = Message.objects.get(pk=message_id)
        except Message.DoesNotExist:
            return HttpJsonResponse({'status': 'ERROR', 'error': 'Not owner.'})

        deleted = False
        if message.sender == user:
            message.sender_deleted_at = now
            deleted = True
        if message.recipient == user:
            message.recipient_deleted_at = now
            deleted = True
        if deleted:
            message.save()
            user.message_set.create(message=_(u"Message successfully deleted."))
            if notification:
                notification.send([user], "messages_deleted", {'message': message,})
        else:
            return HttpJsonResponse({'status': 'ERROR', 'error': 'Not owner.'})
    return HttpJsonOkResponse()


@plato_decorators.is_admin_or_superadmin
@http_decorators.require_GET
def list_templates(request, user_edit):
    return direct_to_template(request,
                              'messages/templates.html',
                              {'templates': MailTemplate.for_user(request.user if user_edit else None),
                               'user_edit': user_edit,
                               'form': TemplateForm(request)})
    
@plato_decorators.is_admin_or_superadmin
@http_decorators.require_GET
def list_my_templates(request, user_edit):
    return direct_to_template(request,
                              'messages/my_templates.html',
                              {'templates': MailTemplate.for_user(request.user if user_edit else None),
                               'user_edit': user_edit,
                               'tabname': 'my_templates',
                               'form': TemplateForm(request)})

@plato_decorators.is_admin_or_superadmin
@http_decorators.require_POST
def save_templates(request):
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON content.')

    try:
        user_edit = int(data['user_edit'])
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON content: user')

    for id, new_data in data['data'].items():
        try:
            template = MailTemplate.objects.get(pk=id)
        except MailTemplate.DoesNotExist:
            pass
        if template.owner is not None and template.owner != request.user:
            raise HttpResponseForbidden()
        assert user_edit or template.owner is None

        if user_edit and new_data.get('save_as_default'):
            # if "save_as_default" is selected in user edit screen,
            # find global, parent template and fill it with the form
            # content too
            tmpl = MailTemplate.objects.get(type=template.type, identifier=template.identifier,
                                            owner=None)
            tmpl.content = new_data['text']
            tmpl.subject = new_data['title']
            tmpl.send_msg = new_data['send_msg']
            tmpl.save()
        if (template.content == new_data['text'] and
            template.subject == new_data['title'] and
            template.send_msg == new_data['send_msg']):
            # skip if no changes were made
            continue
        template.content = new_data['text']
        template.subject = new_data['title']
        template.send_msg = new_data['send_msg']
        if user_edit and template.owner != request.user:
            # "copy-on-write" if saving new user template
            template.pk = None
            template.owner = request.user
        template.save()

    return HttpJsonOkResponse()


def get_upload_filename(upload_name, user):
    user_path = user.username
    upload_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, user_path)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    filename = '{0}-{1}'.format(uuid.uuid4(), upload_name)
    return os.path.join(upload_path, filename), os.path.join(user_path, filename)


@plato_decorators.is_admin_or_superadmin
@http_decorators.require_POST
@csrf_exempt
def upload_image(request):
    upload = request.FILES['upload']
    if '/' in upload.name:
        raise HttpResponseBadRequest('Uploaded file contains invalid characters')
    upload_filename, upload_uri = get_upload_filename(re.sub('[^\w\.-]', '', upload.name).strip(), request.user)
    with open(upload_filename, 'wb') as out:
        for chunk in upload.chunks():
            out.write(chunk)
            
    if settings.CKEDITOR_UPLOAD_WWW_PATH:
        url = settings.CKEDITOR_UPLOAD_WWW_PATH + upload_uri
    else:
        url = settings.CKEDITOR_UPLOAD_URL + upload_uri
        
    return HttpResponse("""
    <script type='text/javascript'>
        window.parent.CKEDITOR.tools.callFunction(%s, '%s');
    </script>""" % (request.GET['CKEditorFuncNum'], url))


def _get_modules(request):
    if request.user.get_profile().role in (
        manage_models.UserProfile.ROLE_SUPERADMIN,
        ):
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(
                coursegroup__group__in=request.user.groups.all())\
                        .distinct().all()
    return courses


def _get_ocl_messages(user, course_id, show_my_links='true'):
    if user.get_profile().is_superadmin:
        if show_my_links == 'true':
            message_list = Message.objects.filter(
                    sender=user,
                    messageprofile__ocl__expired=False)
        else:
            message_list = Message.objects.filter(
                    messageprofile__ocl__expired=False)
    elif user.get_profile().is_admin:
        message_list = Message.objects.filter(
                sender=user,
                messageprofile__ocl__expired=False)
    else:
        return []
 
    if course_id:
        try:
            course = Course.objects.get(pk=course_id)
            message_list = message_list.filter(messageprofile__courses=course)
            course_id = int(course_id)
        except Course.DoesNotExist:
            pass
    
    return message_list


def _get_request_data(request):
    course_id = request.GET.get('course_id', None) or\
            request.COOKIES.get('message_filter_by_course_id', None)
    if course_id is not None:
        course_id = int(course_id)

    ocl_only = request.GET.get('ocl_only', None) or\
            request.COOKIES.get('message_filter_by_ocl_only', None)
    
    show_my_ocl_links = request.GET.get('show_my_ocl_links', None) or\
            request.COOKIES.get('message_filter_by_my_ocl_links_only',
                    None)
    if show_my_ocl_links is None:
        show_my_ocl_links = 'true'

    return {"course_id": course_id, "ocl_only": ocl_only,
            "show_my_ocl_links": show_my_ocl_links}


def _set_response_data(request, response):
    if request.GET.get('course_id', None):
        response.set_cookie('message_filter_by_course_id',
                request.GET.get('course_id'))
    if request.GET.get("ocl_only", None):
        response.set_cookie('message_filter_by_ocl_only',
                request.GET.get('ocl_only'))
    if request.GET.get("show_my_ocl_links", None):
        response.set_cookie('message_filter_by_my_ocl_links_only',
                request.GET.get('show_my_ocl_links'))

    return response

def edit_before_send(request):
    template = ''
    savedTemplateData = False
    data = request.GET.get('template', 'assign_to_all')
    
    templates = { 'assign_to_all': MailTemplate.MSG_IDENT_ADD_MULTI_ASSIGNMENTS,
                  'assign_to_one': MailTemplate.MSG_IDENT_ADD_ASSIGNMENT,
                  'assign_to_one_ocl': MailTemplate.MSG_IDENT_ADD_ASSIGNMENT_OCL }
        
    template = MailTemplate.for_user(request.user,
                             identifier=templates.get(data))[0]
                                 
    if request.method == "POST":
        savedTemplateData = json.loads(request.raw_post_data).get('templateData')
                                 
    return direct_to_template(request, 'messages/dialog/edit_before_send.html',
                          {'template': template,
                           'savedTemplate': savedTemplateData,
                           'templateType': data}) 

def show_preview(request):
    data = {}
    parsed_modules_list = ''
    template = ''
    
    if request.method == "POST":
        data = json.loads(request.raw_post_data)
        
        if data.get('action') == 'remove_user':
            template = MailTemplate.for_user(request.user,
                 identifier=MailTemplate.MSG_IDENT_GOODBYE,
                 type=MailTemplate.TYPE_EMAIL)[0]
        elif data.get('action') == 'edit_user':
            template = MailTemplate.for_user(request.user,
                 identifier=MailTemplate.MSG_IDENT_DATA_EDIT,
                 type=MailTemplate.TYPE_EMAIL)[0]
        elif data.get('action') == 'add_user':
            template = MailTemplate.for_user(request.user,
                 identifier=MailTemplate.MSG_IDENT_WELCOME,
                 type=MailTemplate.TYPE_EMAIL)[0]
    
        return direct_to_template(request, 'messages/dialog/preview.html',
                                  {'notificationBody': template.content}) 
