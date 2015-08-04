# -*- coding: utf-8 -*-

from django.conf.urls import patterns

from views import OAuthView


urlpatterns = patterns(
    '',

    (r'oauth/$', OAuthView.as_view()),
)
