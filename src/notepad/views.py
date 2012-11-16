from datetime import datetime
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.views.generic.simple import direct_to_template
from django.views.decorators import http as http_decorators
from django import http
from django.contrib.auth import models as auth_models, decorators as auth_decorators
import json
from bls_common.bls_django import HttpJsonOkResponse, HttpJsonResponse
from notepad.models import Note
from bls_common import bls_django
from content import serializers

def notepad(request):
    return render_to_response('notepad/notepad.html',
                              {'notes_list': Note.objects.filter(owner=request.user)},
                              context_instance=RequestContext(request))

@auth_decorators.login_required
@http_decorators.require_POST
def save(request):
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return http.HttpResponseBadRequest('Invalid JSON content.')

    if 'note_id' in data:
        note = get_object_or_404(Note, id=data['note_id'], owner=request.user)
    else:
        note = Note(owner=request.user)

    note.content = data['content']
    note.title = data['title']
    note.save()

    return HttpJsonResponse({'status': 'OK',
                             'note_id': note.id,
                             'updated_on': serializers.ts_to_unix(note.updated_on)})

@auth_decorators.login_required
@http_decorators.require_GET
def note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    return bls_django.HttpJsonResponse({"id": note.id,
                                        "title": note.title,
                                        "content": note.content,
                                        "updated_on": serializers.ts_to_unix(note.updated_on)})

@auth_decorators.login_required
@http_decorators.require_POST
def delete(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.delete()
    return bls_django.HttpJsonOkResponse()
