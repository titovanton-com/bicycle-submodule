# coding: UTF-8

from django.db import models


class Variable(models.Model):
    title = models.CharField(max_length=30, verbose_name=u'Имя')
    name = models.CharField(max_length=30, verbose_name=u'Машинное имя')
    value = models.TextField(verbose_name=u'Значение')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['title',]
