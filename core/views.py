# coding: UTF-8

import json

from django.http import Http404
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.base import ContextMixin

from shortcuts import get_page


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


class FilterMixin(object):
    queryset = None

    def get_queryset(self):
        if self.queryset is None and getattr(self, 'model', False):
            return self.model.objects.all()
        return self.queryset

    class FilterError(Exception):
        pass

    def apply_filter(self, request):
        return self.get_queryset()


class PageFilterMixin(FilterMixin):
    paginate = True
    allow_empty = True
    # wtf?
    context_object_name = None
    page_kwarg = 'page'
    page_size_kwarg = 'page-size'
    default_page_size = '6x4'

    def apply_filter(self, request):
        if self.paginate:
            try:
                page_num = int(request.GET.get(self.page_kwarg, 1))
            except ValueError:
                if self.allow_empty:
                    page_num = 1
                else:
                    raise Http404

            try:
                size = request.GET.get(self.page_size_kwarg, self.default_page_size)
                rows, columns = [int(i) for i in size.split('x')]
            except ValueError:
                if self.allow_empty:
                    rows, columns = [int(i) for i in self.default_page_size.split('x')]
                else:
                    raise Http404

            pager = Paginator(self.get_queryset(), rows * columns)

            try:
                page = pager.page(page_num)
            except EmptyPage:
                if self.allow_empty:
                    page = pager.page(pager.num_pages)
                else:
                    raise Http404
            # self.queryset = page.object_list
            self.page = page
            self.rows = rows
            self.columns = columns
            self.page_num = page_num
