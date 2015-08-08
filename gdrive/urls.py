# -*- coding: utf-8 -*-

from django.conf.urls import patterns

from views import OAuthView
from views import TestsView


urlpatterns = patterns(
    '',

    (r'oauth/$', OAuthView.as_view()),
    (r'tests/$', TestsView.as_view()),
)
