from django.contrib.auth.models import Group, User
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from messages.forms import ComposeForm
from messages.models import Message
from django.conf import settings
from models import MailTemplate
import datetime

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


def send_message(sender, recipients_ids, subject, body, parent_msg=None):
    message_list = []
    for r in recipients_ids:
        msg = Message(
                sender=sender,
                recipient=User.objects.get(id=r),
                subject=subject,
                body=body,
                )
        if parent_msg is not None:
            msg.parent_msg = parent_msg
            parent_msg.replied_at = datetime.datetime.now()
            parent_msg.save()
        msg.save()
        message_list.append(msg)
        if notification:
            if parent_msg is not None:
                notification.send([sender], "messages_replied", {'message': msg, })
                notification.send([r], "messages_reply_received", {'message': msg, })
            else:
                notification.send([sender], "messages_sent", {'message': msg, })
                notification.send([r], "messages_received", {'message': msg, })
    return message_list

def send_goodbye_email(recipient):
    send_mail_custom(subject=settings.GOODBYE_EMAIL_SUBJECT, message=settings.GOODBYE_EMAIL_MESSAGE,
              recipient_list=[recipient.email], from_email=settings.DEFAULT_FROM_EMAIL)

def send_email(recipient, msg_ident, msg_data=None):
    template = MailTemplate.objects.get(type=MailTemplate.TYPE_EMAIL, identifier=msg_ident)

    send_mail_custom(subject=template.populate_params_to_text(template.subject, msg_data), message=template.populate_params(msg_data),
              recipient_list=[recipient.email], from_email=settings.DEFAULT_FROM_EMAIL)

def send_mail_custom(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)
    email = EmailMessage(subject, message, from_email, recipient_list,
                        connection=connection)
    email.content_subtype = settings.EMAIL_CONTENT_SUBTYPE
    
    return email.send()