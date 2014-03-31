# coding: UTF-8

from django.conf import settings
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
# from bicycle.djangomixins.shortcuts import get_page

from models import News
from forms import GetPage


class NewsListViewBase(ListView):

    """
    U should to specify News model: model = News (used in __init__)
    """
    paginate_by = getattr(settings, 'NEWS_PER_PAGE', 12)

    def get_queryset(self):
        return super(NewsListViewBase, self).get_queryset().published()

    def get_context_data(self, **kwargs):
        kwargs['breadcrumbs'] = [('/', u'Главная'), 'Новости', ]
        return super(NewsListViewBase, self).get_context_data(**kwargs)


class NewsDetailViewBase(DetailView):

    def get_queryset(self):
        return super(NewsDetailViewBase, self).get_queryset().published()

    def get_context_data(self, **kwargs):
        kwargs['breadcrumbs'] = [('/', u'Главная'), ('/news/', 'Новости'),
                                 self.object.title]
        return super(NewsDetailViewBase, self).get_context_data(**kwargs)


class NewsListView(NewsListViewBase):
    model = News
    template_name = 'news/object_list.html'


class NewsDetailView(NewsDetailViewBase):
    model = News
    template_name = 'news/object.html'
