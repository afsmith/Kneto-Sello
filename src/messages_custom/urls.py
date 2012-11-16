
from django.conf.urls.defaults import *
from messages.views import inbox, outbox, view, delete
import views

urlpatterns = patterns('',
        url(r'^inbox', inbox, {'template_name': 'messages/inbox.html',}, name='messages_inbox'),
        url(r'^outbox', outbox, {'template_name': 'messages/outbox.html',}, name='messages_outbox'),
        url(r'^view/(?P<message_id>\d+)/$', view, name='messages_detail'),
        url(r'^delete/(?P<message_id>\d+)/$', views.delete, name='messages_delete'),
        url(r'^reply/(?P<message_id>\d+)/$', views.reply, name='messages_reply'),
        url(r'^compose/$', views.compose, name="messages_compose"),
        url(r'^templates/$', views.list_templates, name="messages-list_templates"),
        url(r'^templates/save/$', views.save_templates, name="messages-save_templates"),
)