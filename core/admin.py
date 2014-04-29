# coding: UTF-8

from django.contrib import admin
from django.conf import settings


class MetaSeoMixin(object):
    widgets = {
        'html_keywords': admin.widgets.AdminTextareaWidget,
        'html_description': admin.widgets.AdminTextareaWidget,
    }


def make_published(modeladmin, request, queryset):
    rows_updated = queryset.update(published=True)
    modeladmin.message_user(request, 
        "%s объект(ов) успешно опубликован(ы)." % rows_updated)
make_published.short_description = u'Опубликовать'


def make_unpublished(modeladmin, request, queryset):
    rows_updated = queryset.update(published=False)
    modeladmin.message_user(request, 
        "%s объект(ов) успешно снят(ы) с публикации." % rows_updated)
make_unpublished.short_description = u'Убрать флаг публикации'


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


admin.site.add_action(make_published)
admin.site.add_action(make_unpublished)
