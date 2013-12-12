# coding: UTF-8

from django.db import models
from bicycle.djangomixins.models import StandartUnorderedMixin
from bicycle.djangomixins.models import AliasMixin
from bicycle.djangomixins.models import SeoMixin


class NewsBase(StandartUnorderedMixin, AliasMixin, SeoMixin):
    custom_created = models.DateField(verbose_name=u'Дата')
    preview = models.TextField(verbose_name=u'Текст', blank=True)
    text = models.TextField(verbose_name=u'Текст')

    def get_breadcrumbs(self):
        return [('/', u'Главная'), ('/news/', u'Новости'), self.title]

    class Meta:
        abstract = True
        ordering = ['-created']
        verbose_name_plural = u'Новости'
