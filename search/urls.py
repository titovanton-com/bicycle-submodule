# coding: UTF-8

from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns('bicycle.searchextensions.views',
    url(r'^update-index/$', 'update_index'),
)