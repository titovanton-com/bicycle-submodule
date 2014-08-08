# coding: UTF-8

from django.db import models
from bicycle.core.models import PublishedMixin
from bicycle.core.models import SlugMixin
from bicycle.core.models import EditLinkMixin
from bicycle.core.models import SeoMixin
from bicycle.sitemap.models import SiteMapMixin


class NewsBase(PublishedMixin, SlugMixin, SeoMixin):
    custom_created = models.DateField(verbose_name=u'Дата')
    preview = models.TextField(verbose_name=u'Анонс', blank=True)
    text = models.TextField(verbose_name=u'Текст')

    class Meta:
        abstract = True
        ordering = ['-custom_created']
        verbose_name_plural = u'Новости'


class News(NewsBase, SiteMapMixin, EditLinkMixin):
    default_priority = 0.3

    @classmethod
    def get_sitemap_queryset(cls):
        return cls.objects.published()

    def get_breadcrumbs(self):
        return [('/', u'Главная'), ('/news/', u'Новости'), self.title]
