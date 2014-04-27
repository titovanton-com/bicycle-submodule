# coding: UTF-8

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.base import ContextMixin


class ToDoMixin(object):
    todo = None

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            if 'todo' in kwargs:
                method = '%s_%s' % (request.method.lower(), kwargs['todo'])
            elif self.todo is not None:
                method = '%s_%s' % (request.method.lower(), self.todo)
            else:
                method = request.method.lower()
            handler = getattr(self, method, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class RenderWithContextMixin(ContextMixin):

    def response(self, request, template, context, get_context_flag=True):
        context.update({'request': request})
        if get_context_flag:
            context = self.get_context_data(**context)
        return render(request, template, context)

    def redirect(*args, **kwargs):
        return redirect(*args, **kwargs)


class FileResponseMixin(object):

    def file_response(self, file_url, filename):
        response = HttpResponse(mimetype='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response['X-Accel-Redirect'] = file_url
        return response


class ToDoView(ToDoMixin, View):
    pass
