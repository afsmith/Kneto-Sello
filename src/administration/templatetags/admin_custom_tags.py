"""
    Custom tags for displaying customizable application data (footer, header, ...)

    author: Marek Mackiewicz (marek.mackiewicz@blstream.com)
"""

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

from administration.models import ConfigEntry, get_entry



register = template.Library()

TAGS_MAPPINGS = {
    'footer': ConfigEntry.GUI_FOOTER,
    'title': ConfigEntry.GUI_CUSTOM_WEB_TITLE
}

DEFAULT_VALUES_MAPPINGS = {
    ConfigEntry.GUI_FOOTER: settings.DEFAULT_GUI_FOOTER,
    ConfigEntry.GUI_CUSTOM_WEB_TITLE: settings.DEFAULT_GUI_WEB_TITLE,
}


@register.tag(name='admin_tag')
def do_footer_tag(parser, token):
    try:
        key = token.split_contents()[-1]
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    
    try:
        return AdminTag(TAGS_MAPPINGS[key])
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

class AdminTag(template.Node):
    def __init__(self, config_key):
        self._config_key = config_key

    def render(self, context):

        if self._config_key not in context:
            config = get_entry(self._config_key)
            if config:
                context[self._config_key] = config.config_val
            else:
                context[self._config_key] = DEFAULT_VALUES_MAPPINGS[self._config_key]
        return context[self._config_key]

