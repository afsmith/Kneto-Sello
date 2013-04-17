import email
import imaplib
import mimetypes
import poplib
import re
import logging

from datetime import datetime, timedelta
from email.header import decode_header
from email.Utils import parseaddr, collapse_rfc2231_value
from django.conf import settings
from celery.decorators import task
from django.utils.translation import ugettext as _
from messages_custom.models import MessageProfile
from messages.models import Message, signals
from django.utils.html import strip_tags

signals.post_save.receivers = []
logger = logging.getLogger("messages_custom")


@task
def check_mailbox():
    """
    add to settings your pop3 or imap connection settings:

    POP3:
    EMAIL_BOX_TYPE = 'pop3'
    EMAIL_BOX_HOST = 'pop.googlemail.com'
    EMAIL_BOX_PORT = 995
    EMAIL_BOX_USER = 'lusikka.plato@gmail.com'
    EMAIL_BOX_PASSWORD = 'pass'
    EMAIL_BOX_REMOVE_MESSAGES = True
    EMAIL_BOX_SSL = True

    IMAP:
    EMAIL_BOX_TYPE = 'imap'
    EMAIL_BOX_HOST = 'imap.gmail.com'
    EMAIL_BOX_PORT = 993
    EMAIL_BOX_USER = 'lusikka.plato@gmail.com'
    EMAIL_BOX_PASSWORD = 'pass'
    EMAIL_BOX_IMAP_FOLDER = 'INBOX'
    EMAIL_BOX_REMOVE_MESSAGES = True
    EMAIL_BOX_SSL = True
    """
    if settings.EMAIL_BOX_TYPE == 'pop3':
        logger.debug("Checking POP3 mailbox %s" % settings.EMAIL_BOX_USER)
        if settings.EMAIL_BOX_SSL:
            server = poplib.POP3_SSL(settings.EMAIL_BOX_HOST,
                    int(settings.EMAIL_BOX_PORT))
        else:
            server = poplib.POP3(settings.EMAIL_BOX_HOST,
                    int(settings.EMAIL_BOX_PORT))

        server.getwelcome()
        server.user(settings.EMAIL_BOX_USER)
        server.pass_(settings.EMAIL_BOX_PASSWORD)

        messagesInfo = server.list()[1]
        logger.debug("Got %d new messages" % len(messagesInfo))
        for msg in messagesInfo:
            msgNum = msg.split(" ")[0]
            msgSize = msg.split(" ")[1]

            full_message = "\n".join(server.retr(msgNum)[1])
            message_from_email(full_message)
            if settings.EMAIL_BOX_REMOVE_MESSAGES:
                logger.debug("Removing email %s" % msgNum)
                server.dele(msgNum)

        server.quit()

    elif settings.EMAIL_BOX_TYPE == 'imap':
        logger.debug("Checking IMAP mailbox %s" % settings.EMAIL_BOX_USER)
        if settings.EMAIL_BOX_SSL:
            server = imaplib.IMAP4_SSL(settings.EMAIL_BOX_HOST,
                int(settings.EMAIL_BOX_PORT))
        else:
            server = imaplib.IMAP4(settings.EMAIL_BOX_HOST,
                int(settings.EMAIL_BOX_PORT))

        server.login(settings.EMAIL_BOX_USER, settings.EMAIL_BOX_PASSWORD)
        server.select(settings.EMAIL_BOX_IMAP_FOLDER)
        status, data = server.search(None, 'NOT', 'DELETED')

        if data:
            msgnums = data[0].split()
            logger.debug("Got %d new messages" % len(msgnums))
            for num in msgnums:
                status, data = server.fetch(num, '(RFC822)')
                message_from_email(data[0][1])
                if settings.EMAIL_BOX_REMOVE_MESSAGES:
                    logger.debug("Removing email %s" % num)
                    server.store(num, '+FLAGS', '\\Deleted')

        server.expunge()
        server.close()
        server.logout()
        logger.debug("Checking IMAP mailbox %s ... DONE." % settings.EMAIL_BOX_USER)
    else:
        msg = "settings.EMAIL_BOX_TYPE is not set properly"
        logger.error(msg)
        raise Exception(msg)

    logger.debug("Mailbox %s check: done" % settings.EMAIL_BOX_USER)
    return True


def decodeUnknown(charset, string):
    if not charset:
        try:
            return string.decode('utf-8', 'ignore')
        except:
            return string.decode('iso8859-1', 'ignore')
    return unicode(string, charset)


def decode_mail_headers(string):
    decoded = decode_header(string)
    return u' '.join([unicode(msg, charset or 'utf-8')
        for msg, charset in decoded])


def message_from_email(message):
    # 'message' must be an RFC822 formatted message.
    msg = message
    message = email.message_from_string(msg)
    subject = message.get('subject', _('Created from e-mail'))
    subject = decode_mail_headers(decodeUnknown(
        message.get_charset(), subject))
    subject = subject.replace("Re: ", "").replace("Fw: ", "")\
            .replace("RE: ", "").replace("FW: ", "").strip()

    sender = message.get('from', _('Unknown Sender'))
    sender = decode_mail_headers(decodeUnknown(message.get_charset(), sender))
    sender_email = parseaddr(sender)[1]

    header_message_id = message.get('message-id', '')
    header_in_reply_to = message.get('in-reply-to', '')
    
    logger.debug("Got message: From: <%s>, Message-Id: %s, In-Reply-To: %s" %\
            (sender_email, header_message_id, header_in_reply_to))
    logger.debug("Subject: %s" % subject)
    if header_in_reply_to:
        try:
            previous_msg_profile = MessageProfile.objects.get(
                header_message_id=header_in_reply_to)
        except MessageProfile.DoesNotExist:
            logger.warn("Cannot find previous message with header "\
                    "In-Reply-To: %s" % header_in_reply_to)
            return False
    else:
        logger.warn("Email has not In-Reply-To header, dropping it. ")
        return False

    msg_previous = previous_msg_profile.message
    logger.debug("Found parent message. Message id: %s" % msg_previous.id)

    body_plain, body_html = '', ''

    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue

        name = part.get_param("name")
        if name:
            name = collapse_rfc2231_value(name)

        if part.get_content_maintype() == 'text' and name == None:
            if part.get_content_subtype() == 'plain':
                body_plain = decodeUnknown(part.get_content_charset(),
                        part.get_payload(decode=True))
            else:
                body_html = part.get_payload(decode=True)
        else:
            #ignore other content types
            pass

    if body_plain:
        body = body_plain
    elif body_html:
        body = body_html
    else:
        body = ''

    subject = strip_tags(subject)
    body = strip_tags(body)
    now = datetime.now()
    msg = Message(
            sender=msg_previous.recipient,
            recipient=msg_previous.sender,
            subject=subject,
            body=body,
            )
    msg.parent_msg = msg_previous
    msg_previous.replied_at = datetime.now()
    msg_previous.save()
    msg.save()

    msg_profile = MessageProfile(message=msg,
            header_message_id=header_message_id,
            header_in_reply_to=header_in_reply_to)
    msg_profile.save()
    msg_profile.courses.add(*list(previous_msg_profile.courses.all()))
    msg_profile.save()

    logger.debug("Email from %s (%s) properly imported into db. Id: %s" %\
            (msg.sender.email, msg_profile.header_message_id, msg.id))
    return True


if __name__ == '__main__':
    #email_file = open("messages_custom/fixtures/email_html.txt")
    #email_file = open("messages_custom/fixtures/email_plaintext.txt")
    #message_from_email(''.join(email_file.readlines()))
    check_mailbox()
