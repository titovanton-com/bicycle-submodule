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
from django.views.generic.base import RedirectView

from models import DeferManager
from models import OnlyManager
from tools import get_page


class ToDoMixin(object):
    handler_prefix = None
    handler_suffix = None
    todo = None

    def dispatch(self, request, *args, **kwargs):

        if request.method.lower() in self.http_method_names:
            todo = kwargs.pop('todo', '').replace('-', '_')

            if todo not in ['queryset', 'page']:

                if todo:
                    method = '%s_%s' % (request.method.lower(), todo)
                    self.todo = todo
                elif self.todo is not None:
                    method = '%s_%s' % (request.method.lower(), self.todo)
                else:
                    method = request.method.lower()

                if self.handler_prefix is not None:
                    method = '%s_%s' % (self.handler_prefix, method)
                elif self.handler_suffix is not None:
                    method = '%s_%s' % (method, self.handler_suffix)

                handler = getattr(self, method, self.http_method_not_allowed)
                return handler(request, *args, **kwargs)

        handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


class ToDoAjaxMixin(ToDoMixin):

    def dispatch(self, request, *args, **kwargs):

        if request.is_ajax():
            self.handler_prefix = 'ajax'

        return super(ToDoAjaxMixin, self).dispatch(request, *args, **kwargs)


class StatusMixin:

    def status(self, status):
        return HttpResponse(status=status)


class ResponseMixin(StatusMixin, ContextMixin):

    def response(self, request, template, context, **kwargs):
        context.update({'request': request})

        return render(request, template, context, **kwargs)

    def raw_response(self, raw_text, **kwargs):
        return HttpResponse(raw_text, **kwargs)

    def response2(self, request, template, context, **kwargs):
        context.update({'request': request})
        context = self.get_context_data(**context)

        return render(request, template, context, **kwargs)

    def redirect(self, *args, **kwargs):
        return redirect(*args, **kwargs)


class JsonResponseMixin(StatusMixin):

    def json_response(self, data=None, is_json=False, *args, **kwargs):

        if data is not None:

            if not is_json:
                data = json.dumps(data)

            return HttpResponse(data, content_type='application/json')
        else:
            return HttpResponse(*args, content_type='application/json', **kwargs)


class XmlResponseMixin(StatusMixin):

    def xml_response(self, data=None, *args, **kwargs):

        if data is not None:
            return HttpResponse(data, content_type='application/xml')
        else:
            return HttpResponse(*args, content_type='application/xml', **kwargs)


class FileResponseMixin:

    def file_response(self, file_url, filename):
        response = HttpResponse(mimetype='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response['X-Accel-Redirect'] = file_url

        return response


class ToDoView(ToDoMixin, View):
    pass


class ToDoAjaxView(ToDoAjaxMixin, View):
    pass


class FilterMixin:
    queryset = None

    def get_queryset(self):

        if self.queryset is None and getattr(self, 'model', False):

            if isinstance(self.model.objects, DeferManager):
                return self.model.objects.defer_all()
            elif isinstance(self.model.objects, OnlyManager):
                return self.model.objects.only_all()
            else:
                return self.model.objects.all()

        return self.queryset

    class FilterError(Exception):
        pass

    def apply_filter(self, request):
        return self.get_queryset()


class PageFilterMixin(FilterMixin):
    paginate = True
    allow_empty = True
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


class Redirect301View(RedirectView):
    permanent = True


class FilterQuerysetMixin(object):
    '''Must be last in the bases list of mixins with overloaded get_queryset method'''

    model = None

    def get_queryset(self):

        if getattr(self, 'model', False):

            if isinstance(self.model.objects, DeferManager):
                return self.model.objects.defer_all()
            elif isinstance(self.model.objects, OnlyManager):
                return self.model.objects.only_all()
            else:
                return self.model.objects.all()

        else:
            raise FilterQuerysetError('self.model does not specified')

    class FilterQuerysetError(Exception):
        pass


class QuerysetByPageMixin(object):
    '''Must be first in the bases list of mixins with overloaded get_queryset method'''

    paginate = True
    allow_empty = True
    page_kwarg = 'page'
    page_size_kwarg = 'page-size'
    rows_columns = '6x4'
    prefetch_related = []

    def get_queryset(self):
        '''Returns object_list of specified page_num'''

        queryset = super(QuerysetByPageMixin, self).get_queryset()

        if self.paginate:

            # page_num
            try:
                page_num = int(self.request.GET.get(self.page_kwarg, 1))
            except ValueError:
                if self.allow_empty:
                    page_num = 1
                else:
                    raise Http404

            # rows, columns
            try:
                size = self.request.GET.get(self.page_size_kwarg, self.default_page_size)
                rows, columns = [int(i) for i in size.split('x')]
            except ValueError:
                if self.allow_empty:
                    rows, columns = [int(i) for i in self.default_page_size.split('x')]
                else:
                    raise Http404

            pager = Paginator(queryset, rows * columns)

            # page
            try:
                page = pager.page(page_num)
            except EmptyPage:
                if self.allow_empty:
                    page = pager.page(pager.num_pages)
                else:
                    raise Http404

            self.page = page
            self.rows = rows
            self.columns = columns
            self.page_num = page_num
            return page.object_list

    def get_context_data(self, **kwargs):
        '''Use object_list instead page.object_list in template
        if you want to prefetch_related,
        else - does not metter'''

        object_list = self.get_queryset()

        if self.prefetch_related:
            object_list = object_list.prefetch_related(*self.prefetch_related)

        context = {
            'object_list': object_list,
            'page': self.page,
            'rows': self.rows,
            'columns': self.columns,
            'page_num': self.page_num,
        }
        context.update(kwargs)
        return context
