# coding: UTF-8
"""
:mod:`bicycle.djangomixins.models.models` -- main models mixins collection
===================================

.. moduleauthor:: Titov Anton (mail@titovanton.com)
"""
import os
import inspect

from django.db import models
from django.http import Http404
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.html import escape
from django.conf import settings
from sorl.thumbnail.fields import ImageField
from sorl.thumbnail import get_thumbnail

from bicycle.djangomixins.utilites import valid_alias
from bicycle.djangomixins.utilites import upload_file
from bicycle.djangomixins.utilites import upload_logo


class DynamicMethodsMixin(object):
    """This mixin provide passing arguments to class object method, using method name.

    For example: if your object *obj* has method with name *do_it* and it takes two ordered 
    arguments with names *age* and *growth*, then you can construct name for a method call,
    using double underscore: 
    ::
        obj.do_it__28__185()
    very usefull in djanto templates:
    ::
        {{ obj.do_it__28__185 }}
    """

    class __MethodWrapper(object):

        def __init__(self, this, method, *args):
            self.__this = this
            self.__args = args
            self.__method = method

        def __call__(self, *args):
            args = args or self.__args
            return self.__method(self.__this, *args)

    def __getattribute__(self, name):
        try:
            spr = super(DynamicMethodsMixin, self).__getattribute__(name)
        except AttributeError:
            msg = '\'%s\' object has no attribute \'%s\'' % (self.__class__.__name__, name)
            try:
                l = name.split('__')
                method_name, args = l[0], l[1:]
            except IndexError:
                raise AttributeError(msg)
            else:
                methods = dict(inspect.getmembers(self.__class__, inspect.ismethod))
                if method_name in methods:
                    return self.__MethodWrapper(self, methods[method_name], *args)
                else:
                    raise AttributeError(msg)
        else:
            return spr


class GetUrlMixin(object):

    def get_url(self):
        return u'/%s/%s/' % (self.__class__.__name__.lower(), self.alias)

    def get_url_with_app(self):
        return u'/%s/%s/%s/' % (self._meta.app_label, self.__class__.__name__.lower(), self.alias)

    def get_url_by_pk(self):
        return u'/%s/pk/%s/' % (self.__class__.__name__.lower(), self.pk)
        
    def get_url_with_app_by_pk(self):
        return u'/%s/%s/pk/%s/' % (self._meta.app_label, self.__class__.__name__.lower(), self.pk)


class EditLinkMixin(object):

    def get_admin_link(self):
        return u'/admin/%s/%s/%s/' % (self._meta.app_label, self.__class__.__name__.lower(),
                                      self.pk)


class UnicodeAliasMixin(object):

    def __unicode__(self):
        if self.alias:
            return u'%s' % self.alias
        else:
            return u'%s with pk: %s' % (self.__class__.__name__, self.pk)


class UnicodeTitleAliasMixin(object):

    def __unicode__(self):
        if settings.DEBUG and self.alias or not self.title and self.alias:
            return u'%s' % self.alias
        elif self.title:
            return u'%s' % self.title
        else:
            return u'%s with pk: %s' % (self.__class__.__name__, self.pk)


class TitleMixin(models.Model):
    title = models.CharField(max_length=128, verbose_name=u'Название')

    class Meta:
        abstract = True


class UnicodeTitleMixin(object):

    def __unicode__(self):
        return u'%s with title: %s' % (self.__class__.__name__, self.title)


class AliasRequiredMixin(TitleMixin, GetUrlMixin, UnicodeAliasMixin, EditLinkMixin):
    alias = models.CharField(max_length=128, unique=True, verbose_name=u'Название латиницей')

    def save(self):
        self.alias = valid_alias(self.alias)
        super(AliasRequiredMixin, self).save()

    class Meta:
        abstract = True


class AliasNotRequiredMixin(TitleMixin, GetUrlMixin, UnicodeAliasMixin, EditLinkMixin):
    alias = models.CharField(max_length=128, unique=True, blank=True, null=True,
                             verbose_name=u'Название латиницей')

    def save(self):
        if not self.alias:
            self.alias = valid_alias(self.title)
        else:
            self.alias = valid_alias(self.alias)
        super(AliasNotRequiredMixin, self).save()

    class Meta:
        abstract = True


class ImgSeoMixin(models.Model):
    image_title = models.CharField(max_length=128, blank=True,
                                   verbose_name=u'Атрибут изображения title')
    image_alt = models.CharField(max_length=128, blank=True,
                                 verbose_name=u'Атрибут изображения alt')

    class Meta:
        abstract = True


class LogoMixin(ImgSeoMixin):
    logo = ImageField(upload_to=upload_logo, verbose_name=u'Лого')

    def logo_admin(self):
        if self.logo.name:
            image_path = os.path.join(settings.MEDIA_ROOT, str(self.logo))
        else:
            image_path = os.path.join(settings.MEDIA_ROOT, 'noimage.png')
        try:
            thumbnail = get_thumbnail(image_path, '100x100', quality=20)
        except IOError:
            return u'Лого нет'
        else:
            return u'<a href="%s/"><img src="%s"/></a>' % (self.pk, thumbnail.url)
    logo_admin.short_description = u'Лого'
    logo_admin.allow_tags = True

    class Meta:
        abstract = True


class PublishedQuerySet(models.query.QuerySet):

    def get_published(self, **kwargs):
        return self.get(published=True, **kwargs)

    def get_published_or_404(self, **kwargs):
        try:
            return self.get(published=True, **kwargs)
        except self.model.DoesNotExist:
            raise Http404('No %s matches the given query.' % self.model._meta.object_name)

    def get_unpublished(self, **kwargs):
        return self.get(published=False, **kwargs)

    def published(self, **kwargs):
        return self.filter(published=True, **kwargs)

    def unpublished(self, **kwargs):
        return self.filter(published=False, **kwargs)


class PublishedManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return PublishedQuerySet(self.model, using=self._db)

    def get_published(self, **kwargs):
        return self.get_query_set().get_published(**kwargs)

    def get_published_or_404(self, **kwargs):
        qs = self.get_query_set()
        try:
            return qs.get_published(**kwargs)
        except qs.model.DoesNotExist:
            raise Http404('No %s matches the given query.' % qs.model._meta.object_name)

    def get_unpublished(self, **kwargs):
        return self.get_query_set().get_unpublished(**kwargs)

    def published(self, **kwargs):
        return self.get_query_set().published(**kwargs)

    def unpublished(self, **kwargs):
        return self.get_query_set().unpublished(**kwargs)


class StandartQuerySet(PublishedQuerySet):

    def __order(self, qs):
        return qs.annotate(null_order_by=models.Count('order_by'))\
                 .order_by('-null_order_by', 'order_by', '-created')

    def published(self, **kwargs):
        return self.__order(super(StandartQuerySet, self).published(**kwargs))

    def unpublished(self, **kwargs):
        return self.__order(super(StandartQuerySet, self).unpublished(**kwargs))


class StandartManager(PublishedManager):

    def get_query_set(self):
        return StandartQuerySet(self.model, using=self._db)


class ChronologyMixin(models.Model):
    created = models.DateTimeField(verbose_name=u'Создан')
    updated = models.DateTimeField(verbose_name=u'Обновлен')

    def save(self):
        if not self.id:
            self.created = now()
        self.updated = now()
        super(ChronologyMixin, self).save()

    class Meta:
        ordering = ['-created', ]
        abstract = True


class StandartMixin(ChronologyMixin):
    published = models.BooleanField(verbose_name=u'Опубликован', default=True)
    order_by = models.IntegerField(null=True, blank=True, verbose_name=u'Порядок в списке')

    objects = StandartManager()

    class Meta:
        ordering = ['order_by', '-created']
        abstract = True


class StandartUnorderedMixin(ChronologyMixin):
    published = models.BooleanField(verbose_name=u'Опубликован')

    objects = PublishedManager()

    class Meta:
        abstract = True


class SeoMixin(models.Model):
    html_title = models.CharField(max_length=256, blank=True,
                                  verbose_name=u'Название вкладки')
    html_keywords = models.CharField(max_length=512, blank=True,
                                     verbose_name=u'Ключевики для поисковых систем')
    html_description = models.TextField(blank=True,
                                        verbose_name=u'Описание для поисковых систем')

    class Meta:
        abstract = True


class ImageBase(ImgSeoMixin):
    published = models.BooleanField(verbose_name=u'Опубликован')
    order_by = models.IntegerField(null=True, blank=True, verbose_name=u'Порядок в списке')
    image = ImageField(upload_to=upload_file, verbose_name=u'Изображение')

    objects = PublishedManager()

    def thumbnail_admin(self):
        if self.image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, str(self.image))
        else:
            image_path = os.path.join(settings.MEDIA_ROOT, 'noimage.png')
        try:
            thumbnail = get_thumbnail(image_path, '100x100', quality=20)
        except IOError:
            return u'Изображения нет'
        else:
            return u'<a href="%s/"><img src="%s"/></a>' % (self.pk, thumbnail.url)
    thumbnail_admin.short_description = u'Thumbnail'
    thumbnail_admin.allow_tags = True

    def image_html(self):
        if len(self.image):
            code = u'<img class="img-responsive" alt="%s" title="%s" src="%s"/>' % \
                   (self.image_alt, self.image_title, self.image.url)
            return escape(code)
        else:
            return u'Изображения нет'

    def image_py(self):
        if len(self.image):
            code = u'<img class="img-responsive" alt="%s" title="%s" \
                     src="{{ MEDIA_URL }}%s"/>' % \
                   (self.image_alt, self.image_title, self.image.name)
            return escape(code)
        else:
            return u'Изображения нет'

    def __unicode__(self):
        return u'%s with pk: %s' % (self.__class__.__name__, self.pk)

    class Meta:
        ordering = ['order_by', '-pk']
        verbose_name_plural = u'Изображения'
        abstract = True


class CategoryBase(AliasRequiredMixin, LogoMixin, SeoMixin):
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=u'Предок')

    def get_breadcrumbs(self):
        breadcrumbs = [(self.title,)]
        tmp = self
        while tmp.parent is not None:
            tmp = tmp.parent
            breadcrumbs = [(tmp.get_url(), tmp.title)] + breadcrumbs
        return [('/', u'Главная')] + breadcrumbs

    def get_branch(self):
        pass

    class Meta:
        verbose_name_plural = u'Категории'
        abstract = True
