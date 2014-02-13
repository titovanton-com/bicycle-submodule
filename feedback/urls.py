# -*- coding: utf-8 -*-

from django.conf.urls import patterns
from django.conf.urls import url

from views import FeedbackCreateView


urlpatterns = patterns('',
    url(r'^$', FeedbackCreateView.as_view()),
)
