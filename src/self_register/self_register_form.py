from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from self_register.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from management.models import UserProfile
from management import models
from administration.models import get_entry_val, ConfigEntry
from django.contrib.auth.models import Group, User

attrs_dict = {'class': 'required'}


class SelfRegisterForm(RegistrationForm):
    required_css_class = 'formList label'
    username = forms.CharField(label=_('Username'),
            max_length=UserProfile.USERNAME_LENGTH)
    email = forms.EmailField(label=_('Email'))
    email_repeat = forms.EmailField(label=_('Repeat email'))
    first_name = forms.CharField(label=_('First name'),
            max_length=UserProfile.FIRST_NAME_LENGTH)
    last_name = forms.CharField(label=_('Last name'),
            max_length=UserProfile.LAST_NAME_LENGTH)
    language = forms.ChoiceField(label=_('Language'),
            choices=settings.AVAILABLE_LANGUAGES)
    token = forms.CharField(label=_('Token'))
    group = forms.ModelChoiceField(queryset=Group.objects.order_by('name').filter(\
            id__in=models.GroupProfile.objects.filter(
                self_register_enabled=True)))

    password1 = forms.CharField(label=_('New password'),
                                   required=True,
                                   widget=forms.PasswordInput(),
                                   min_length=5,
                                   max_length=20)
    password2 = forms.CharField(required=True,
                                       widget=forms.PasswordInput(),
                                       min_length=5,
                                       max_length=20,
                                       label=_('Repeat new password'))

    def clean_email(self):
        email = self.cleaned_data["email"]
        users = User.objects.filter(email__iexact=email).all()
        if len(users) > 0:
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return email

    def clean_token(self):
        reg_token = get_entry_val(ConfigEntry.SELF_REGISTER_TOKEN)
        if (self.cleaned_data.get('token') != reg_token):
            raise forms.ValidationError(_("Invalid Token."))
        return self.cleaned_data.get('token')
    
    def clean_email_repeat(self):
        """
        Verifiy that the values entered into the two email fields
        match.
        
        """
        if 'email' in self.cleaned_data and 'email_repeat' in self.cleaned_data:
            if self.cleaned_data['email'] != self.cleaned_data['email_repeat']:
                raise forms.ValidationError(_("The two email fields didn't match."))
        return self.cleaned_data['email_repeat']
    
