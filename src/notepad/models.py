
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth_models

class Note(models.Model):

    title = models.CharField(_('Title'), max_length=120, null=False)
    content = models.TextField(_('Content'), null=False)
    owner = models.ForeignKey(auth_models.User, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_on',)