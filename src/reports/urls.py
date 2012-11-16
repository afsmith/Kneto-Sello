from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
        url(r'^$', views.reports, name='reports-reports'),
        url(r'^get_details/$', views.get_details, name='reports-get_details'),
        url(r'^get_details/(?P<id>\d+)/$', views.get_details, name='reports-get_details'),
        url(r'^create/$', views.reports_create, name='reports-create'),
        url(r'^create/(?P<id>\d+)/$', views.reports_create, name='reports-edit'),
        url(r'^delete/(?P<id>\d+)/$', views.reports_delete, name='reports-delete'),
        url(r'^list/$', views.reports_list, name='reports-list'),
        url(r'^generate/(?P<id>\d+)/$', views.generate, name='reports-generate'),
)