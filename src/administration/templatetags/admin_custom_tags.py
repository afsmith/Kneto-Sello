"""
    Custom tags for displaying customizable application data (footer, header, ...)

    author: Marek Mackiewicz (marek.mackiewicz@blstream.com)
"""

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from os import path

from administration.models import ConfigEntry, get_entry, get_entry_val



register = template.Library()

TAGS_MAPPINGS = {
    'footer': ConfigEntry.GUI_FOOTER,
    'title': ConfigEntry.GUI_CUSTOM_WEB_TITLE,
    'logo_as_title': ConfigEntry.GUI_LOGO_AS_TITLE,
    'logo': ConfigEntry.GUI_LOGO_FILE,
    'background': ConfigEntry.GUI_BG_FILE,
    'use_bg_image': ConfigEntry.GUI_IMAGE_AS_BG,
}

FILE_TAG_MAPPINGS = {
    'background': settings.CUSTOM_BG_FILE_NAME
}

DEFAULT_VALUES_MAPPINGS = {
    ConfigEntry.GUI_FOOTER: settings.DEFAULT_GUI_FOOTER,
    ConfigEntry.GUI_CUSTOM_WEB_TITLE: settings.DEFAULT_GUI_WEB_TITLE,
    ConfigEntry.GUI_LOGO_FILE: settings.DEFAULT_LOGO_FILE_NAME,
}


@register.filter(name='htmlattributes')
def htmlattributes(value, arg):
    attrs = value.field.widget.attrs
    data = arg.replace(' ', '')   
    kvs = data.split(',') 

    for string in kvs:
        kv = string.split(':')
        attrs[kv[0]] = kv[1]

    rendered = str(value)

    return rendered

@register.filter(name="is_checked")
def is_checked(key):
    logo_entry = get_entry(TAGS_MAPPINGS[key])
    if logo_entry and logo_entry.config_val == 'False':
        return False
    return (logo_entry and logo_entry.config_val) or False

@register.filter(name='has_extension')
def has_extension(file_name):
    return (path.splitext(file_name)[-1] and True) or False

@register.simple_tag
def get_url(key):
    """ get_url
         get url for customized files
    """
    url = settings.CSS_TEMPLATES_URL +'/'+ FILE_TAG_MAPPINGS[key]
    return url

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
                if self._config_key == TAGS_MAPPINGS['logo']:
                    gui_logo_filename = get_entry_val(ConfigEntry.GUI_LOGO_FILE) or ''
                    gui_logo_filename_parts = path.splitext(gui_logo_filename)
                    gui_logo_file_ext = gui_logo_filename_parts[1] or ''
                    logo_file_url = ''
                    if gui_logo_filename:
                        logo_file_url = settings.CSS_TEMPLATES_URL +'/'+ \
                                        settings.CUSTOM_LOGO_FILE_NAME + \
                                        gui_logo_file_ext
                    context[self._config_key] = logo_file_url
                    return context[self._config_key]

                context[self._config_key] = config.config_val
            else:
                context[self._config_key] = DEFAULT_VALUES_MAPPINGS[self._config_key]
        return context[self._config_key]

