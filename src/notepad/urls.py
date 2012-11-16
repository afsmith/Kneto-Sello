
from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
        url(r'^$', views.notepad, name='notepad-notepad'),
        url(r'^save/$', views.save, name='notepad-save'),
        url(r'^notes/(?P<note_id>\d+)/$', views.note, name='notepad-note'),
        url(r'^notes/(?P<note_id>\d+)/delete/$', views.delete, name='notepad-delete'),
)