from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views
from self_register.views import activate, register
from self_register.self_register_form import SelfRegisterForm
from self_register.reset_password_form import PasswordResetForm

urlpatterns = patterns('',
    url(r'^register/$', register, {
        'form_class': SelfRegisterForm,
        'backend': 'self_register.backends.RegisterBackend'
        }, name='registration_register'),
    url(r'^register/complete/$', direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    url(r'^activate/complete/$', direct_to_template,
        {'template': 'registration/activation_complete.html'},
        name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', activate,
        {'backend': 'self_register.backends.RegisterBackend'},
        name='registration_activate'),
    url(r'^register/closed/$', direct_to_template,
        {'template': 'registration/registration_closed.html'},
        name='registration_disallowed'),
    url(r'^password/reset/$', auth_views.password_reset, {
            'template_name': 'registration/password_reset_form.html',
            'password_reset_form': PasswordResetForm,
        },
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'template_name': 'registration/password_reset_confirm.html'},
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        {'template_name': 'registration/password_reset_complete.html'},
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        {'template_name': 'registration/password_reset_done.html'},
        name='auth_password_reset_done'),
)
