# -*- coding: utf-8 -*-

from django.db import models


class SiteMapModel(models.Model):
    PRIORITY_CHOICES = (
        (-1, u'По умолчанию'),
        (0.0, 0.0),
        (0.1, 0.1),
        (0.2, 0.2),
        (0.3, 0.3),
        (0.4, 0.4),
        (0.5, 0.5),
        (0.6, 0.6),
        (0.7, 0.7),
        (0.8, 0.8),
        (0.9, 0.9),
        (1.0, 1.0),
    )

    priority = models.FloatField(default=-1, choices=PRIORITY_CHOICES,
                                 verbose_name=u'Приоритет sitemap.xml')

    default_priority = 0.5

    @classmethod
    def get_sitemap_queryset(cls):
        return cls.objects.all()

    def get_priority(self):
        if self.priority == -1:
            return u'%s' % self.default_priority
        else:
            return u'%s' % self.priority

    class Meta:
        abstract = True
