from datetime import datetime
import json
from smtplib import SMTPConnectError, SMTPException
from messages.forms import ComposeForm
from messages.models import Message
from messages.utils import format_quote

from django.conf import settings
from django.contrib.auth import models as auth_models, decorators as auth_decorators
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound
from django.template.context import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.views.decorators import http as http_decorators
from django.views.generic.simple import direct_to_template

from bls_common.bls_django import HttpJsonOkResponse, HttpJsonResponse
from forms import CustomComposeForm, TemplateForm
from models import MailTemplate
from utils import send_message
from plato_common import decorators as plato_decorators


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

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
def compose(request):
    if request.method == "POST":
        try:
            data = json.loads(request.raw_post_data)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON content.')
        send_message(request.user, data['recipients'], data['subject'], data['body'])
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

@plato_decorators.is_admin_or_superadmin
@http_decorators.require_GET
def list_templates(request):
    return direct_to_template(request,
                              'messages/templates.html',
                              {'templates': MailTemplate.objects.all(),
                               'form': TemplateForm(request)})


@plato_decorators.is_admin_or_superadmin
@http_decorators.require_POST
def save_templates(request):
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON content.')

    for id, new_data in data['data'].items():
        try:
            template = MailTemplate.objects.get(pk=id)
        except MailTemplate.DoesNotExist:
            pass

        template.content = new_data['text']
        template.subject = new_data['title']
        template.save()
    
    return HttpJsonOkResponse()