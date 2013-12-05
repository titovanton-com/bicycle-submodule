# coding: UTF-8

from django.conf import settings
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
# from bicycle.djangomixins.shortcuts import get_page

# from models import News
# from forms import GetPage


class NewsListBase(ListView):

    """
    U have to specify News model: model = News (used in __init__)
    """
    paginate_by = getattr(settings, 'NEWS_PER_PAGE', 12)

    def get_queryset(self):
        return super(NewsListBase, self).get_queryset().published()

    def get_context_data(self, **kwargs):
        kwargs['breadcrumbs'] = [('/', u'Главная'), 'Новости', ]
        return super(NewsListBase, self).get_context_data(**kwargs)


class NewsDetailBase(DetailView):
    slug_field = 'alias'
    slug_url_kwarg = 'alias'

    def get_queryset(self):
        return super(NewsDetailBase, self).get_queryset().published()

    def get_context_data(self, **kwargs):
        kwargs['breadcrumbs'] = [('/', u'Главная'), ('/news/', 'Новости'),
                                 self.object.title]
        return super(NewsDetailBase, self).get_context_data(**kwargs)
