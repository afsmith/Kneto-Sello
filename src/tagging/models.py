
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth_models
import content
from content.models import File

TYPE_CUSTOM = 0
TYPE_GROUP = 1
TYPE_OWNER = 2
TAG_TYPES = (
    (TYPE_CUSTOM, 'custom'),
    (TYPE_GROUP, 'group'),
    (TYPE_OWNER, 'owner')
)

tag_val = models.CharField(_('Tag entry value'), max_length=255)

class Tag(models.Model):
    name = models.CharField(_('tag name'), max_length=255)
    is_default = models.BooleanField(_('is default'), default=False)
    type = models.IntegerField(_('tag type'), choices=TAG_TYPES, null=True)
    
    files = models.ManyToManyField(File)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
def get_tag_label(key):
    for type in TAG_TYPES:
        if type[0] == key: return type[1]
    return get_tag_label(TYPE_CUSTOM)