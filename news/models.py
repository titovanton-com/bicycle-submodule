# coding: UTF-8

from django.db import models
from bicycle.djangomixins.models import PublishedMixin
from bicycle.djangomixins.models import SlugMixin
from bicycle.djangomixins.models import SeoMixin


class NewsBase(PublishedMixin, SlugMixin, SeoMixin):
    custom_created = models.DateField(verbose_name=u'Дата')
    preview = models.TextField(verbose_name=u'Анонс', blank=True)
    text = models.TextField(verbose_name=u'Текст')

    def get_breadcrumbs(self):
        return [('/', u'Главная'), ('/news/', u'Новости'), self.title]

    class Meta:
        abstract = True
        ordering = ['-custom_created']
        verbose_name_plural = u'Новости'


class News(NewsBase):
    pass
