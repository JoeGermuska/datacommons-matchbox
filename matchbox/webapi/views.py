import datetime
try:
    import json
except ImportError:
    import simplejson as json
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from matchbox.api import LocalClient

client = LocalClient('datacommons')

def _querydict_to_dict(qd):
    d = {}
    for k,l in qd.iterlists():
        if len(l) == 1:
            l = l[0]
        d[str(k)] = l
    return d

def _jsonize(data):
    if isinstance(data, list):
        return [_jsonize(i) for i in data]

    for k,v in data.iteritems():
        if isinstance(v, datetime.datetime):
            data[k] = str(v)
    return data

def entity(request, uid=None):
    data = None
    if request.method == 'POST':
        if uid:
            key = client.update(uid,  **_querydict_to_dict(request.POST))
        else:
            try:
                key = client.insert(_querydict_to_dict(request.POST))
            except TypeError, e:
                return HttpResponseBadRequest(str(e))
        data = {'id':key}
    elif request.method == 'GET':
        if uid:
            data = client.get(uid)
        else:
            data = list(client.search(**_querydict_to_dict(request.GET)))

    return HttpResponse(json.dumps(_jsonize(data)))

@require_POST
def make_merge(request):
    name = request.POST.get('name')
    ids = request.POST.getlist('id')
    source = request.POST.get('source')
    _type = request.POST.get('type')

    if not name:
        return HttpResponseBadRequest('missing required parameter "name"')
    if not ids or len(ids) < 2:
        return HttpResponseBadRequest('must specify two or more id parameters to merge')

    data = client.make_merge(name, ids, source, _type)

    return HttpResponse(json.dumps(_jsonize(data)))

@require_POST
def commit_merge(request):
    merge_record = _querydict_to_dict(request.POST)
    new_id = client.commit_merge(merge_record)
    return HttpResponse(json.dumps({'id':new_id}))
