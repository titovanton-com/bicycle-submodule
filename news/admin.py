# coding: UTF-8
# Копипаста

from django.contrib import admin
from django import forms
from bicycle.djangomixins.admin import MetaSeoMixin

from models import News


def make_published(modeladmin, request, queryset):
    queryset.update(published=True)


def make_unpublished(modeladmin, request, queryset):
    queryset.update(published=False)


class myNewsAdminForm(forms.ModelForm):
    class Meta(MetaSeoMixin):
        model = News


class NewsAdmin(admin.ModelAdmin):
    form = myNewsAdminForm
    list_display = ('title', 'alias', 'published', 'created', 'updated',)
    actions = [make_published, make_unpublished,]
    readonly_fields = ('created', 'updated')
    search_fields = ('title',)
    fieldsets = (
        (u'Основное', {'fields': ('title', 'alias', 'published', 'custom_created', 
                                  'preview', 'text')}),
        (u'SEO', {'fields': ('html_title', 'html_keywords', 'html_description',)}),
        (u'Хронология', {'fields': ('created', 'updated',)}),
    )


admin.site.register(News, NewsAdmin)