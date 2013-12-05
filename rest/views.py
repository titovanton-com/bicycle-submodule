# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse


class JsonResponseMixin(object):

    def response(self, data, is_json=False):
        if not is_json:
            data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')
