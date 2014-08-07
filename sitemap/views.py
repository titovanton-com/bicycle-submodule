# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models.loading import get_model
from django.views.generic import TemplateView
from bicycle.core.utilites import site_wild_classes

from models import SiteMapMixin


class SitemapView(TemplateView):
    template_name = ['sitemap.xml', 'sitemap/base.xml']
    content_type = 'application/xhtml+xml'

    def get_template_names(self):
        # I have to reload this method, becouse of bug/error in TemplateView code
        return self.template_name

    def get_queryset(self, model):
        return model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(SitemapView, self).get_context_data(**kwargs)
        context['object_list'] = site_wild_classes('models', SiteMapMixin)
        return context
