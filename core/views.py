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


<<<<<<< HEAD
class QuerysetFilterMixin(object):

    def apply_filter(self, request, **kwargs):
        return self.queryset


class PageFilterMixin(QuerysetFilterMixin):
    object_list_kwarg = 'object_list'
    page_kwarg = 'page'
    page_size_kwarg = 'page_size'
    start_page = 1
    default_page_size = '3x3'

    class PageFilterError(Exception):
        pass

    def _valid_page(self, request):
        try:
            page = int(request.GET.get(self.page_kwarg, self.start_page))
        except ValueError:
            page = self.start_page
        return page

    def _valid_page_size(self, request):
        page_size = request.GET.get(self.page_size_kwarg, self.default_page_size)
        try:
            width, height = page_size.split('x')
            width, height = int(width), int(height)
        except ValueError:
            width, height = self.default_page_size.split('x')
            width, height = int(width), int(height)
        return width, height

    def apply_filter(self, request, **kwargs):
        super(PageFilterMixin, self).apply_filter(request, **kwargs)
        page_num = self._valid_page(request)
        width, height = self._valid_page_size(request)
        pager = Paginator(self.queryset, width * height)
        try:
            self.page = pager.page(page_num)
        except EmptyPage:
            self.page = pager.page(pager.num_pages)
        self.page.width, self.page.height = width, height

    def get_context_data(self, **kwargs):
        c = super(PageFilterMixin, self).get_context_data(**kwargs)
        try:
            c['page'] = self.page
            c['object_list'] = self.page.object_list
        except AttributeError:
            raise PageFilterError('You must to invocation apply_filter to initial self.page')
        return c
=======
class FilterMixin(object):
    queryset = None

    def apply_filter(self, request):
        return self.queryset


class PageFilterMixin(FilterMixin):
    allow_empty = True
    context_object_name = None
    page_kwarg = 'page'
    size_kwarg = 'page_size'
    default_size = '3x4'

    def apply_filter(self, request):
        try:
            page_num = int(request.GET.get(self.page_kwarg, 1))
        except ValueError:
            if self.allow_empty:
                page_num = 1
            else:
                raise Http404

        try:
            size = request.GET.get(self.size_kwarg, self.default_size)
            width, height = [int(i) for i in size.split('x')]
        except ValueError:
            if self.allow_empty:
                width, height = [int(i) for i in self.default_size.split('x')]
            else:
                raise Http404

        print width, height
        pager = Paginator(self.queryset, width * height)

        try:
            page = pager.page(page_num)
        except EmptyPage:
            if self.allow_empty:
                page = pager.page(pager.num_pages)
            else:
                raise Http404
        self.queryset = page.object_list
        self.page = page
        self.width = width
        self.height = height
        self.page_num = page_num
>>>>>>> 736b6f8
