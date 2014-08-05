# -*- coding: utf-8 -*-

from django.conf.urls import patterns

from views import SitemapView


urlpatterns = patterns('',
    (r'^sitemap\.xml', SitemapView.as_view()),
)
