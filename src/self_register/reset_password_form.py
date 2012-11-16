from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django.utils.http import int_to_base36
from management import models


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        """
        email = self.cleaned_data.get("email", None)

        allowed_users = []
        users = User.objects.filter(email__iexact=email).all()
        for user in users:
            profile = user.get_profile()
            if profile.role == models.UserProfile.ROLE_USER:
                allowed_users.append(user)

        if len(allowed_users) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't "\
                    "have an associated user account. Are you sure you've "\
                    "registered?"))
        elif len(allowed_users) == 1:
            self.user = allowed_users[0]
        else:
            raise forms.ValidationError(_("More than one user account use "\
                    "this e-mail. You should report it to an administrator."))
        return self.cleaned_data

    def save(self, domain_override=None,
            email_template_name='registration/password_reset_email.html',
            use_https=False, token_generator=default_token_generator,
            request=None):
        """
        Generates a one-use only link for resetting password and sends to
        the user
        """
        from django.core.mail import send_mail

        user = getattr(self, 'user', None)
        if user:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            send_mail(_("Password reset on %s") % site_name,
                    t.render(Context(c)), None, [user.email])
