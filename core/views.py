# coding: UTF-8

import json

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.base import ContextMixin


class ToDoMixin(object):
    todo = None

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            if 'todo' in kwargs and kwargs['todo']:
                todo = kwargs['todo'].replace('-', '_')
                method = '%s_%s' % (request.method.lower(), todo)
            elif self.todo is not None:
                method = '%s_%s' % (request.method.lower(), self.todo)
            else:
                method = request.method.lower()
            handler = getattr(self, method, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class StatusMixin(object):

    def status(self, status):
        return HttpResponse(status=status)


class ResponseMixin(StatusMixin, ContextMixin):

    def response(self, request, template, context, get_context_flag=True, **kwargs):
        context.update({'request': request})
        if get_context_flag:
            context = self.get_context_data(**context)
        return render(request, template, context, **kwargs)

    def redirect(*args, **kwargs):
        return redirect(*args, **kwargs)


class JsonResponseMixin(StatusMixin):

    def json_response(self, data=None, is_json=False, *args, **kwargs):
        if data is not None:
            if not is_json:
                data = json.dumps(data)
            return HttpResponse(data, content_type='application/json')
        else:
            return HttpResponse(*args, content_type='application/json', **kwargs)


class FileResponseMixin(object):

    def file_response(self, file_url, filename):
        response = HttpResponse(mimetype='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response['X-Accel-Redirect'] = file_url
        return response


class ToDoView(ToDoMixin, View):
    pass
