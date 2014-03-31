# -*- coding: utf-8 -*-

from django.conf.urls import patterns
from django.conf.urls import url

from views import NewsListView
from views import NewsDetailView


urlpatterns = patterns('',
    url(r'^(?P<slug>[^/]*)/$', NewsDetailView.as_view()),
    url(r'^$', NewsListView.as_view()),
)
