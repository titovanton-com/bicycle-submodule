# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models.loading import get_model
from django.views.generic import TemplateView


class SitemapView(TemplateView):
    template_name = ['sitemap.xml', 'sitemap/base.xml']
    content_type = 'application/xhtml+xml'

    def get_template_names(self):
        # I have to reload this method, becouse of bug/error in TemplateView code
        return self.template_name

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
                'priority': sitemap[key].get('priority', 0.5),
                'ids': sitemap[key].get('ids', {})
            }
            context['object_list'] += (obj,)
            context['DOMAIN'] = settings.DOMAIN
        return context
