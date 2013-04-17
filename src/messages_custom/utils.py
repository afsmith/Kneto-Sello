from django.contrib.auth.models import Group, User
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage, make_msgid
from messages.forms import ComposeForm
from messages.models import Message, signals
from django.template.loader import render_to_string
from django.conf import settings
from models import MailTemplate, MessageProfile
import datetime
from django.utils.translation import ugettext as _
import logging

logger = logging.getLogger("messages_custom")

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

####################################################################
#override new_message_email call
signals.post_save.receivers = []
####################################################################


def send_message(sender, recipients_ids, subject, body, parent_msg=None,
        courses=None, ocl=None, template_name="messages/new_message.html",
        attachments=None):

    message_list = []
    for r in recipients_ids:
        recipient = User.objects.get(id=r)
        if recipient is not None:
            # support for generic "first name" and "last name" params for all templates
            subject = subject.replace('[first name]', recipient.first_name)
            subject = subject.replace('[last name]', recipient.last_name)
            body = body.replace('[first name]', recipient.first_name)
            body = body.replace('[last name]', recipient.last_name)
            
        msg = Message(
                sender=sender,
                recipient=User.objects.get(id=r),
                subject=subject,
                body=body,
                )
        
        parent_msg_profile = None
        if parent_msg is not None: 
            try:
                parent_msg_profile = MessageProfile.objects.get(
                        message=parent_msg)
            except MessageProfile.DoesNotExist:
                pass

            msg.parent_msg = parent_msg
            parent_msg.replied_at = datetime.datetime.now()
            parent_msg.save()
        msg.save()
        
        #get course from parent_msg
        header_msg_id = make_msgid()
        if not courses:
            courses = []
            if parent_msg_profile:
                courses = parent_msg_profile.courses.all()
        
        msg_profile = MessageProfile(message=msg,
                header_message_id=header_msg_id)

        if parent_msg_profile:
            msg_profile.header_in_reply_to = parent_msg_profile.header_message_id
        msg_profile.save()
        msg_profile.courses.add(*courses)
        msg_profile.ocl = ocl
        msg_profile.save()
            
        if msg.recipient.email != "":
            reply_to = _get_reply_to_field(msg.sender)
            from_field = _get_from_field(msg.sender)

            message = render_to_string(template_name, {
                'message': msg,
                })
            try:
                send_mail_custom(subject=msg.subject, message=message,
                    recipient_list=[msg.recipient.email],
                    from_email=from_field,
                    headers={
                        "Reply-To": reply_to,
                        "Message-Id": header_msg_id
                        },
                    attachments=attachments)
            except Exception, e:
                logger.error("Error while sending email: %s" % e)
                raise e
        
        message_list.append(msg)
        
        if notification:
            if parent_msg is not None:
                notification.send([sender], "messages_replied", {'message': msg, })
                notification.send([r], "messages_reply_received", {'message': msg, })
            else:
                notification.send([sender], "messages_sent", {'message': msg, })
                notification.send([r], "messages_received", {'message': msg, })
    return message_list


def resend_message(msg):
        msg_profile = MessageProfile.objects.get(message=msg)
        if msg.recipient.email != "":
            reply_to = _get_reply_to_field(msg.sender)
            from_field = _get_from_field(msg.sender)

            try:
                return send_mail_custom(subject=msg.subject, message=msg.body,
                    recipient_list=[msg.recipient.email],
                    from_email=from_field,
                    headers={
                        "Reply-To": reply_to,
                        "Message-Id": msg_profile.header_message_id
                        })
            except Exception, e:
                logger.error("Error while sending email: %s" % e)
                raise e


def send_email(recipient, msg_ident, msg_data=None, user=None, courses=None,
        ocl=None, prevent_user_plus=True, template_content=None,
        template_subject=None):
    if prevent_user_plus and recipient.get_profile().is_user_plus:
        return

    template = MailTemplate.for_user(user, type=MailTemplate.TYPE_EMAIL, identifier=msg_ident)[0]
    if template_subject:
        subject = template.populate_params_to_text(template_subject, msg_data)
    else:
        subject = template.populate_params_to_text(template.subject, msg_data)
    if template_content:
        body = template.populate_params_to_text(template_content, msg_data)
    else:
        body = template.populate_params(msg_data)

    send_message(subject=subject,
                    body=body,
                    recipients_ids=[recipient.id],
                    sender=user,
                    courses=courses,
                    ocl=ocl)


def send_mail_custom(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, headers={}, attachments=None):
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)
    email = EmailMessage(subject.strip(), message, from_email.strip(), recipient_list,
                        connection=connection, headers=headers,
                        attachments=attachments)
    email.content_subtype = settings.EMAIL_CONTENT_SUBTYPE
    return email.send()

def _get_reply_to_field(user):
    reply_to = [settings.DEFAULT_FROM_EMAIL]
    if user:
        reply_to.append(user.email)
    return ', '.join(reply_to)


def _get_from_field(user):
    if user:
        user_profile = user.get_profile()
        if user_profile.is_superadmin or user_profile.is_admin:
            from_field = "%s %s <%s>" % (user.first_name, user.last_name,\
                    user.email)
        else:
            from_field = "%s %s <%s>" % (user.first_name, user.last_name,\
                    settings.DEFAULT_FROM_EMAIL)
    else:
        from_field = settings.DEFAULT_FROM_EMAIL
    
    return from_field
