
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth_models
import content
from content.models import File

class Tag(models.Model):
    name = models.CharField(_('tag name'), max_length=255)
    is_default = models.BooleanField(_('is default'), default=False)
    
    files = models.ManyToManyField(File)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name