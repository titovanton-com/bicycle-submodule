# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _


def false_icon():
    return u'<img alt="False" src="%sadmin/img/icon-no.gif">' % settings.STATIC_URL


def true_icon():
    return u'<img alt="True" src="%sadmin/img/icon-yes.gif">' % settings.STATIC_URL


class MetaSeoMixin:
    widgets = {
        'html_keywords': admin.widgets.AdminTextareaWidget,
        'html_description': admin.widgets.AdminTextareaWidget,
    }


def make_published(modeladmin, request, queryset):
    rows_updated = queryset.update(published=True)
    modeladmin.message_user(
        request,
        _(u'%s object(s) successfull published.') % rows_updated)


def make_unpublished(modeladmin, request, queryset):
    rows_updated = queryset.update(published=False)
    modeladmin.message_user(
        request,
        _(u'%s object(s) successfull unpublished.') % rows_updated)


make_published.short_description = _(u'Publish')
make_unpublished.short_description = _(u'Unpublish')
admin.site.add_action(make_published)
admin.site.add_action(make_unpublished)


class MediaTranslationMeta(type):

    def __new__(cls, name, bases, attrs):
        new = super(MediaTranslationMeta, cls).__new__(cls, name, bases, attrs)
        new.js = (
            'http://yandex.st/jquery/2.0.3/jquery.min.js',
            'http://yandex.st/jquery-ui/1.10.3/jquery-ui.min.js',
            '%smodeltranslation/js/tabbed_translation_fields.js' % settings.STATIC_URL,
        )
        new.css = {
            'screen': ('%smodeltranslation/css/tabbed_translation_fields.css' %
                       settings.STATIC_URL,),
        }
        return new


class RedirectOnSaveMixin:

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(obj.get_url())

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(obj.get_url())
