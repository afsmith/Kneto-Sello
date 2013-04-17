
from django.conf.urls.defaults import *
from messages.views import inbox, outbox, view, delete
import views

urlpatterns = patterns('',
        url(r'^inbox', views.inbox, name='messages_inbox'),
        url(r'^outbox', views.outbox, name='messages_outbox'),
        url(r'^ocl', views.ocl, name='messages_ocl'),
        url(r'^view/(?P<message_id>\d+)/$', views.view, name='messages_detail'),
        url(r'^delete/(?P<message_id>\d+)/$', views.delete, name='messages_delete'),
        url(r'^delete-multiple/$', views.delete_multiple, name='messages_delete_multiple'),
        url(r'^preview/$', views.show_preview, name='messages_show_preview'),
        url(r'^reply/(?P<message_id>\d+)/$', views.reply, name='messages_reply'),
        url(r'^resend/(?P<message_id>\d+)/$', views.resend, name='messages_resend'),
        url(r'^compose/$', views.compose, name="messages_compose"),
        url(r'^templates/$', views.list_templates, kwargs={'user_edit': False}, name="messages-list_templates"),
        url(r'^templates/edit-beforesend/$', views.edit_before_send, name="messages-edit-before-send"),
        url(r'^my_templates/$', views.list_my_templates, kwargs={'user_edit': True}, name="messages-list_my_templates"),
        url(r'^templates/user/$', views.list_templates, kwargs={'user_edit': True}, name="messages-list_user_templates"),
        url(r'^templates/save/$', views.save_templates, name="messages-save_templates"),
        url(r'^upload-image/$', views.upload_image, name="messages-upload-image"),
)
