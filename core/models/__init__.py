# -*- coding: utf-8 -*-
"""
.. moduleauthor:: Titov Anton (mail@titovanton.com)
"""
from datetime import datetime
import inspect
import os
import pytz
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.apps import apps
from django.http import Http404
from django.utils.html import escape
from django.utils.translation import ugettext as _

from sorl.thumbnail import get_thumbnail

from bicycle.core.tools import UploadToDir
from bicycle.core.tools import valid_slug

from .fields import ExifLessImageField as ImageField


DB_MAX_INT = 2147483647

DB_MIN_INT = -2147483648

DB_MAX_SMALL = 32767

DB_MIN_SMALL = -32768


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

    class __MethodWrapper:

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
            msg = '\'%s\' object has no attribute \'%s\'' % (
                self.__class__.__name__, name)

            try:
                l = name.split('__')
                method_name, args = l[0], l[1:]
            except IndexError:
                raise AttributeError(msg)
            else:
                methods = dict(
                    inspect.getmembers(self.__class__, inspect.ismethod))

                if method_name in methods:
                    return self.__MethodWrapper(self, methods[method_name], *args)
                else:
                    raise AttributeError(msg)

        else:
            return spr


class ClassNameMixin(object):

    def app_label(self):
        return self._meta.app_label

    def class_name(self):

        if self._meta.proxy:
            return self._meta.proxy_for_model.__name__

        return self.__class__.__name__


class GetUrlMixin(ClassNameMixin):

    def get_url(self):
        return u'/%s/%s/' % (self.class_name().lower(), self.slug)

    def get_absolute_url(self):
        return settings.URL + self.get_url()


class EditLinkMixin(ClassNameMixin):

    def get_admin_link(self):
        return u'/admin/%s/%s/%s/' % (self.app_label(), self.class_name().lower(),
                                      self.pk)


class UnicodeTitleSlugMixin(ClassNameMixin):

    def __unicode__(self):

        if settings.DEBUG and self.slug or not self.title and self.slug:
            return u'%s' % self.slug
        elif self.title:
            return u'%s' % self.title
        else:
            return u'%s with pk: %s' % (self.class_name(), self.pk)


class TitleModel(ClassNameMixin, models.Model):
    title = models.CharField(max_length=256, verbose_name=_(u'Title'))

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        abstract = True


class UnicodeSlugMixin(ClassNameMixin):

    def __unicode__(self):

        if self.slug:
            return u'%s' % self.slug
        else:
            return u'%s with pk: %s' % (self.class_name(), self.pk)


class SlugModel(GetUrlMixin, EditLinkMixin, UnicodeSlugMixin, TitleModel):
    slug = models.SlugField(max_length=256, unique=True,
                            verbose_name=_(u'Short slug for URL'))

    def save(self, *args, **kwargs):
        self.slug = valid_slug(self.slug)
        super(SlugModel, self).save()

    class Meta:
        abstract = True


class OnlySlugModel(GetUrlMixin, EditLinkMixin, UnicodeSlugMixin, models.Model):
    slug = models.SlugField(max_length=256, unique=True,
                            verbose_name=_(u'Short unique label/slug'))

    def save(self, *args, **kwargs):
        self.slug = valid_slug(self.slug)
        super(OnlySlugModel, self).save()

    class Meta:
        abstract = True


class SlugBlankModel(GetUrlMixin, EditLinkMixin, UnicodeSlugMixin, TitleModel):
    slug = models.SlugField(max_length=256, unique=True, blank=True, null=True,
                            verbose_name=_(u'Short slug for URL'))

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = valid_slug(self.title)
        else:
            self.slug = valid_slug(self.slug)

        super(SlugBlankModel, self).save()

    class Meta:
        abstract = True


class ImgSeoModel(models.Model):
    image_title = models.CharField(max_length=256, blank=True,
                                   verbose_name=_(u'Attribute title of the tag <img/>'))
    image_alt = models.CharField(max_length=256, blank=True,
                                 verbose_name=_(u'Attribute alt of the tag <img/>'))

    class Meta:
        abstract = True


def thumbnail_admin(self, img, pk):

    if img.name:
        image_path = os.path.join(settings.MEDIA_ROOT, str(img))

        try:
            thumbnail = get_thumbnail(image_path, '100x100', quality=80)
        except IOError:
            url = u'http://dummyimage.com/100x100/e0e0e0/de0000.jpg&text=IOError'
        else:
            url = thumbnail.url

    else:
        url = u'http://dummyimage.com/100x100/e0e0e0/545454.jpg&text=dummy'

    return u'<a href="%s/"><img src="%s"/></a>' % (pk, url)


def image_html(self, img):

    if img.name:
        code = u'<img class="img-responsive" alt="%s" title="%s" src="%s"/>' % \
               (self.image_alt, self.image_title, img.url)

        return escape(code)
    else:
        url = u'http://dummyimage.com/100x100/e0e0e0/545454.jpg&text=dummy'

        return u'<img src="%s"/>' % url


class CoverMixin(models.Model):

    def cover_admin(self):

        return thumbnail_admin(self, self.cover, self.pk)

    cover_admin.short_description = u'Обложка'
    cover_admin.allow_tags = True

    class Meta:
        abstract = True


class CoverModel(CoverMixin, ImgSeoModel):
    cover = ImageField(upload_to=UploadToDir('cover'), verbose_name=_(u'Cover'))

    class Meta:
        abstract = True


class CoverBlankModel(CoverMixin, ImgSeoModel):
    cover = ImageField(blank=True, upload_to=UploadToDir('cover'), verbose_name=_(u'Cover'))

    class Meta:
        abstract = True


class PublishedQuerySet(models.query.QuerySet):

    def get_published(self, **kwargs):
        kwargs['published'] = True
        return self.get(**kwargs)

    def get_published_or_404(self, **kwargs):
        kwargs['published'] = True

        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            raise Http404('No %s matches the given query.' %
                          self.model._meta.object_name)

    def get_unpublished(self, **kwargs):
        kwargs['published'] = False
        return self.get(**kwargs)

    def published(self, **kwargs):
        kwargs['published'] = True
        return self.filter(**kwargs)

    def unpublished(self, **kwargs):
        kwargs['published'] = False
        return self.filter(**kwargs)


class PublishedManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db)

    def get_published(self, **kwargs):
        return self.get_queryset().get_published(**kwargs)

    def get_published_or_404(self, **kwargs):
        qs = self.get_queryset()

        try:
            return qs.get_published(**kwargs)
        except qs.model.DoesNotExist:
            raise Http404('No %s matches the given query.' %
                          qs.model._meta.object_name)

    def get_unpublished(self, **kwargs):
        return self.get_queryset().get_unpublished(**kwargs)

    def published(self, **kwargs):
        return self.get_queryset().published(**kwargs)

    def unpublished(self, **kwargs):
        return self.get_queryset().unpublished(**kwargs)


class OrderedQuerySetMixin(object):

    def __order(self, qs):
        return qs.annotate(null_order_by=models.Count('order_by'))\
                 .order_by('-null_order_by', 'order_by', '-pk')

    def filter(self, **kwargs):
        return self.__order(super(OrderedQuerySetMixin, self).filter(**kwargs))

    def all(self, **kwargs):
        return self.__order(super(OrderedQuerySetMixin, self).all(**kwargs))


class ChronologyModel(models.Model):
    created = models.DateTimeField(verbose_name=_(u'Created'))
    updated = models.DateTimeField(verbose_name=_(u'Updated'))

    def save(self, *args, **kwargs):

        if not self.id:
            self.created = datetime.now(pytz.timezone(settings.TIME_ZONE))

        self.updated = datetime.now(pytz.timezone(settings.TIME_ZONE))

        super(ChronologyModel, self).save()

    def full_clean(self, exclude=None, validate_unique=True):

        if exclude is not None:
            exclude += ['created', 'updated']
        else:
            exclude = ['created', 'updated']

        super(ChronologyModel, self).full_clean(exclude, validate_unique)

    class Meta:
        ordering = ['-created', ]
        abstract = True


class PublishedModel(models.Model):
    published = models.BooleanField(verbose_name=_(u'Flag as published'), default=True)

    objects = PublishedManager()

    class Meta:
        abstract = True


class PositionModel(models.Model):
    position = models.PositiveIntegerField(default=DB_MAX_INT, verbose_name=_(u'Order in a list'))

    class Meta:
        ordering = ['position', '-pk']
        abstract = True


class SeoModel(models.Model):
    html_title = models.CharField(max_length=256, blank=True,
                                  verbose_name=_(u'Tab title'))
    html_keywords = models.TextField(blank=True,
                                     verbose_name=_(u'Keywords for search systems'))
    html_description = models.TextField(blank=True,
                                        verbose_name=_(u'Description for search systems'))

    class Meta:
        abstract = True


class ImageBase(EditLinkMixin, ImgSeoModel, PositionModel):
    image = ImageField(upload_to=UploadToDir(), verbose_name=_(u'Image'))

    def thumbnail_admin(self):
        return thumbnail_admin(self, self.image, self.pk)

    thumbnail_admin.short_description = u'Thumbnail'
    thumbnail_admin.allow_tags = True

    def image_html(self):
        return image_html(self, self.image)

    def image_py(self):

        if len(self.image):
            code = u'<img class="img-responsive" alt="%s" title="%s" \
                     src="{{ MEDIA_URL }}%s"/>' % \
                   (self.image_alt, self.image_title, self.image.name)

            return escape(code)
        else:
            return _(u'No image')

    def __unicode__(self):
        return u'%s with pk: %s' % (self.class_name(), self.pk)

    class Meta:
        ordering = ['position', '-pk']
        verbose_name_plural = _(u'Images')
        abstract = True


class CategoryBase(SlugModel, CoverModel, SeoModel):
    parent = models.ForeignKey(
        'self', null=True, blank=True, verbose_name=_(u'Parent'))

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
        verbose_name_plural = _(u'Categories')
        abstract = True


class CoupleBase(TitleModel):
    value = models.CharField(max_length=256, verbose_name=_(u'Value'))

    class Meta:
        abstract = True


class ParseMediaMixin(DynamicMethodsMixin):

    """The mixin provide ability to inject an images and other snippets, such as video to a text.

    Invocing in template:
    ::
        {{ object.parse__description }}

    where description - model field.

    Tags specification:
    ::
        [[ mainapp.Image:kitty ]]
    where mainapp - the app label, Image - the class of model with name Image and
    kitty - the slug of an object.

    .. note::
        An Image object must have to_html method which returns text/html.

    ::
        [[ mainapp.Image:kitty:src ]]
    this one returns only path to a file and invoce to_src insted of to_html.

    .. note::
        An Image object must have to_src method which returns text/html.

    .. note::
        - Parse method return empty string if an attribute does not exists.
        - If an object does not exists or does not have slug attribute or does
        not have to_html attribute, then the parser leave tag without replace.
        - It also uses django cache system, so you have to delete cache every
        time after save an Image object. There is the handler for that.
    """

    LOCAL_CACHE_KEY_PREFIX = 'parse-media:'
    LOCAL_CACHE_TIMEOUT = settings.CACHE_TIMEOUT

    def parse(self, field):

        try:
            text = getattr(self, field)
        except AttributeError:
            return ''

        cmld_to_html = re.compile(
            r'(?P<tag>\[\['
            r'\s*(?P<content>(?P<model>\w+?\.\w+?)\:(?P<slug>[0-9a-zA-Z-_]+?)'
            r'(?P<src>:src)?)'
            r'\s*\]\])')

        for m in cmld_to_html.finditer(text):
            d = m.groupdict()
            key = self.LOCAL_CACHE_KEY_PREFIX + d['content']
            c = cache.get(key)

            if c is not None:
                replacement = c

            else:

                try:
                    model = apps.get_model(d['model'])
                    obj = model.objects.get(slug=d['slug'])

                    if d['src'] is None:
                        replacement = obj.to_html()

                    else:
                        replacement = obj.to_src()

                except (LookupError, AttributeError, FieldError, ObjectDoesNotExist):
                    continue

                cache.set(key, replacement, self.LOCAL_CACHE_TIMEOUT)

            text = text.replace(d['tag'], replacement)

        return text


class ParseMediaCacheMixin(object):

    """
    Usage:
    ::
        from django.db.models.signals import pre_delete
        from django.db.models.signals import pre_save


        pre_save.connect(SomeModel.clear_cached_tag, sender=SomeModel)
        pre_delete.connect(SomeModel.clear_cached_tag, sender=SomeModel)

    ..note::
        It must have media_tag and to_html methods
    """

    LOCAL_CACHE_KEY_PREFIX = 'parse-media:'
    LOCAL_CACHE_TIMEOUT = settings.CACHE_TIMEOUT

    @classmethod
    def clear_cached_tag(cls, sender, **kwargs):
        obj = kwargs['instance']

        if obj.pk:
            old_obj = cls.objects.get(pk=obj.pk)
            key = cls.LOCAL_CACHE_KEY_PREFIX + cls.media_tag(old_obj)[3:-3]
            cache.delete(key)


class ImageMedia(ParseMediaCacheMixin, ImageBase):

    """
    Read ParseMediaCacheMixin and ParseMediaMixin usage
    """

    slug = models.SlugField(max_length=256, unique=True,
                            verbose_name=_(u'Short slug for URL'))

    def media_tag(self):
        return u'[[ %s.%s:%s ]]' % (self.app_label(), self.class_name(), self.slug)

    def media_tag_src(self):
        return u'[[ %s.%s:%s:src ]]' % (self.app_label(), self.class_name(), self.slug)

    def to_html(self):

        if len(self.image):
            code = u'<img class="img-responsive" alt="%s" title="%s" src="%s"/>' % \
                   (self.image_alt, self.image_title, self.image.url)

            return code
        else:
            return ''

    def to_src(self):

        if len(self.image):
            return self.image.url
        else:
            return ''

    class Meta:
        ordering = ['position', '-pk']
        verbose_name_plural = _(u'Images')
        abstract = True


class OnlyManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(OnlyManager, self).get_queryset().only(*self.model.only_fields)


class DeferManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(DeferManager, self).get_queryset().defer(*self.model.defer_fields)


class OnlyManagerModel(models.Model):

    ''' All fields will be defered except in only_fields which is tuple or list '''
    objects = OnlyManager()
    only_fields = []

    class Meta:
        abstract = True


class DeferManagerModel(models.Model):

    ''' All fields from only_fields which is tuple or list will be defered '''
    objects = DeferManager()
    defer_fields = []

    class Meta:
        abstract = True
