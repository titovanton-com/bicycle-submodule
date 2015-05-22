# -*- coding: utf-8 -*-

from django.apps import apps
from django.conf import settings
from django.db.models.loading import get_model
from django.views.generic import TemplateView

from models import SiteMapModel


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
        context['object_list'] = [model for model in apps.get_models()
                                  if issubclass(model, SiteMapModel)]

        if self.request.META['SERVER_PORT'] == 443:
            context['SERVER_PROTOCOL'] = 'https'
        else:
            context['SERVER_PROTOCOL'] = 'http'

        return context
