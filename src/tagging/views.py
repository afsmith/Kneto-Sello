from difflib import SequenceMatcher
import json


from django import http

from django.conf import settings
from django.views.decorators import http as http_decorators

from bls_common import bls_django
from plato_common import decorators
from tagging.models import Tag
from tagging.utils import to_autocomplete_format

@decorators.is_admin_or_superadmin
@http_decorators.require_POST
def create_tag(request):

    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')

    tag_name = data["name"].upper()

    try:
        tag = Tag.objects.get(name=tag_name)
        return bls_django.HttpJsonResponse({'status': 'ERROR',
                                            'messages': 'Tag with name %s already exists' % tag_name,
                                            'tag_id': tag.id})
    except Tag.DoesNotExist:
        is_default = "is_default" in data and data["is_default"]
        tag = Tag.objects.create(name=tag_name, is_default=is_default)
        return bls_django.HttpJsonResponse({'status': 'OK', 'tag_id': tag.id})

@decorators.is_admin_or_superadmin
@http_decorators.require_GET
def autocomplete(request):
    term = request.GET.get('term')

    tags = map(to_autocomplete_format, list(Tag.objects.filter(name__istartswith=term, is_default=False).values(u'pk', u'name')))

    if tags:
        return bls_django.HttpJsonResponse(tags)
    else:
        if not settings.SPELL_CHECKER_ENABLED or len(term) < settings.SPELL_CHECKER_MIN_TERM_LENGTH:
            return bls_django.HttpJsonResponse([])

        result = []
        for tag in list(Tag.objects.all()):
            if SequenceMatcher(None, tag.name, term.upper()).ratio() >= settings.SPELL_CHECKER_MIN_RATIO:
                result.append({u'id': tag.pk, u'value': tag.name})
        return bls_django.HttpJsonResponse(result)