from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from django.contrib.auth.models import Group, User

from self_register import signals
from self_register.models import RegistrationManager
from self_register.models import RegistrationProfile
from management.models import UserProfile
from management import forms, models
from django.shortcuts import get_object_or_404


# Python 2.7 has an importlib with import_module; for older Pythons,
# Django's bundled copy provides it.
try:  # pragma: no cover
    from importlib import import_module  # pragma: no cover
except ImportError:  # pragma: no cover
    from django.utils.importlib import import_module  # pragma: no cover


def get_backend(path):
    """
    Return an instance of a registration backend, given the dotted
    Python import path (as a string) to the backend class.

    If the backend cannot be located (e.g., because no such module
    exists, or because the module does not contain a class of the
    appropriate name), ``django.core.exceptions.ImproperlyConfigured``
    is raised.

    """
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured(
                'Error loading registration backend %s: "%s"' % (module, e))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "%s" does not define a registration backend named "%s"'\
                    % (module, attr))
    return backend_class()


class RegisterBackend(object):

    def register(self, request, **kwargs):
        """
        Extension for Django-registration
        """
        username, email, password, first_name, last_name =\
                kwargs['username'], kwargs['email'], kwargs['password1'],\
                kwargs['first_name'], kwargs['last_name'],

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(
                username, email, password, site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)

        user = User.objects.get(username=new_user.username)
        user.first_name = kwargs['first_name']
        user.last_name = kwargs['last_name']

        user.groups.add(kwargs['group'])
        user.save()

        profile = models.UserProfile(
            user=user,
            role='30',
            language=kwargs['language'])
        profile.save()

        return new_user

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.

        """
        return ('registration_complete', (), {})

    def activate(self, request, activation_key):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the signal
        ``registration.signals.user_activated`` will be sent, with the
        newly activated ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.

        """
        activated = RegistrationProfile.objects.activate_user(activation_key)
        if activated:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated,
                                        request=request)
        return activated

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def post_activation_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        account activation.

        """
        return ('registration_activation_complete', (), {})
