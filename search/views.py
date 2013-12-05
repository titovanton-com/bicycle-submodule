# coding: UTF-8

from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic import ListView
from django.core.context_processors import csrf
from haystack.query import SearchQuerySet
from haystack.query import EmptySearchQuerySet
from bicycle.rest.views import JsonResponseMixin
import django_rq

from utilites import make_search_queryset
from forms import SearchForm


def update_index(request):
    func = 'bicycle.searchextensions.jobs.update_index'
    django_rq.enqueue(func)
    try:
        return redirect(request.META['HTTP_REFERER'])
    except KeyError:
        return redirect('/')


class SearchViewBase(ListView):

    '''
    .. sectionauthor:: Василий Шередеко (piphon@gmail.com)
    '''
    queryset_class = SearchQuerySet
    empty_queryset_class = EmptySearchQuerySet
    search_form = SearchForm
    query = None

    def get_queryset(self):
        form = self.search_form(self.request.GET)
        if form.is_valid():
            self.query = form.cleaned_data['q']
            return make_queryset(self.query, queryset_class=self.queryset_class,
                                 empty_queryset_class=self.empty_queryset_class)
        else:
            return self.empty_queryset_class()

    def get_context_data(self, *args, **kwargs):
        context = super(SearchViewBase, self).get_context_data(*args, **kwargs)
        context.update({
            'query': self.query,
            'search_query': query,
            'result_objects': context['object_list'],
        })
        return context


class RestSearchViewBase(JsonResponseMixin, View):
    queryset_class = SearchQuerySet
    empty_queryset_class = EmptySearchQuerySet
    search_form = SearchForm
    query = None
    resource = None

    def _get_bundle_list(self):
        form = self.search_form(self.request.GET)
        if form.is_valid():
            self.query = form.cleaned_data['q']
            qs = make_search_queryset(self.query, queryset_class=self.queryset_class,
                                      empty_queryset_class=self.empty_queryset_class)
            bundles = []
            res = self.resource()
            for obj in qs:
                bundle = res.build_bundle(obj=obj.object, request=self.request)
                bundles.append(res.full_dehydrate(bundle, for_list=True))
            return bundles
        else:
            return []

    def get(self, request, *args, **kwargs):
        res = self.resource()
        bs = self._get_bundle_list()
        data = {}
        data['meta'] = {}
        data['meta']['total_count'] = len(bs)
        data['meta']['csrf_header_name'] = 'X-CSRFToken'
        data['meta']['csrf_header_value'] = csrf(request)['csrf_token']
        data['objects'] = bs
        return self.response(res.serialize(None, data, "application/json"), True)
