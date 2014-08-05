# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models.loading import get_model
from django.views.generic import TemplateView


class SitemapView(TemplateView):
    template_name = ['sitemap.xml', 'sitemap/base.html']

    def get_settings(self):
        return settings.SITEMAP

    def get_queryset(self, model):
        return model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(SitemapView, self).get_context_data(**kwargs)
        sitemap = self.get_settings()
        context['object_list'] = ()
        for key in sitemap:
            tmp = key.split('.')
            model = get_model(*tmp)
            obj = {
                'queryset': self.get_queryset(model),
                'priority': sitemap[key]['priority'],
                'ids': sitemap[key]['ids']
            }
            context['object_list'] += (obj,)
        return context
