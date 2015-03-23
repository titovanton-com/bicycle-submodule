# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse


class JsonResponseMixin:

    def response(self, data=None, is_json=False, *args, **kwargs):
        if data is not None:
            if not is_json:
                data = json.dumps(data)
            return HttpResponse(data, content_type='application/json')
        else:
            return HttpResponse(*args, content_type='application/json', **kwargs)
