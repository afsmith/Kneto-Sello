
from django.conf.urls.defaults import *

from tagging import views

urlpatterns = patterns('',
    url(r'^tags/create/$', views.create_tag, name='tracking-create_tag'),
    url(r'^tags/autocomplete/$', views.autocomplete, name='tracking-autocomplete'),
)