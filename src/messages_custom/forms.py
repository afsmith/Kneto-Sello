
from django import forms
from django.utils.translation import ugettext_lazy as _

class CustomComposeForm(forms.Form):
    subject = forms.CharField(label=_(u"Subject"), widget=forms.TextInput(attrs={'maxlength': 120}))
    body = forms.CharField(label=_(u"Body"), widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))
    recipients_ids = forms.CharField(max_length=200, widget=forms.HiddenInput)
    course_id = forms.CharField(max_length=200, widget=forms.HiddenInput, required=False)

class TemplateForm(forms.Form):
    content = forms.CharField(label=_(u"Content"), widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))
