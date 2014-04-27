# coding: UTF-8

from django.db import models
from bicycle.core.models import SlugMixin
from bicycle.core.models import LogoMixin
from bicycle.core.models import SeoMixin
from bicycle.core.utilites import machine_word
from bicycle.core.utilites import transliterate
from bicycle.core.shortcuts import true_icon
from bicycle.core.shortcuts import false_icon


class TagBase(SlugMixin):
    description = models.TextField(verbose_name=u'Описание', blank=True)

    def description_admin(self):
        return self.description and true_icon() or false_icon()
    description_admin.short_description = u'Шаблонное описание'
    description_admin.allow_tags = True

    class Meta:
        verbose_name_plural = u'Теги'
        abstract = True


class TagsSetBase(SlugMixin):
    # u should set tags field as in example bellow:
    # tags = models.ManyToManyField(Tag, verbose_name=u'Набор тегов')
    tags = None
    # u should set tags field as in example bellow:
    # sys_tag = models.ForeignKey(Tag, blank=True, null=True, related_name='sys_tag_set')
    sys_tag = None
    parent = models.ForeignKey('self', verbose_name=u'Предок', blank=True, null=True)

    def parent_admin(self):
        return self.parent and self.parent.title or false_icon()
    parent_admin.short_description = u'Предок'
    parent_admin.allow_tags = True

    def make_sys_title(self):
        return u'Системный тег для <%s>' % self.title

    def make_sys_slug(self):
        return machine_word(transliterate(u'system tag ID:%s' % self.pk))

    def save(self):
        super(TagsSetBase, self).save()
        if self.sys_tag is None:
            title = self.make_sys_title()
            slug = self.make_sys_slug()
            tag_model = self._meta.get_field_by_name('tags')[0].rel.to
            sys_tag = tag_model(title=title, slug=slug)
            sys_tag.save()
            self.sys_tag = sys_tag
        super(TagsSetBase, self).save()

    class Meta:
        verbose_name_plural = u'Наборы тегов'
        abstract = True


class TagProductBase(models.Model):

    """
        In perfect world, when u edit Product object in the django admin and attach a tags to,
        the description of a tag automaticly past in textarea. And u can edit description without
        consequences: the description of choosen tag object will be the same.
    """
    # u have to set this field
    product = None
    # u should rewrite tag field, if u use custom Tag model
    # tag = models.ForeignKey(Tag, verbose_name=u'Тег')
    tag = None
    description = models.TextField(verbose_name=u'Описание', blank=True)

    def product_admin(self):
        return self.product.title
    product_admin.short_description = u'Продукт'
    product_admin.allow_tags = True

    def tag_admin(self):
        return self.tag.title
    tag_admin.short_description = u'Тег'
    tag_admin.allow_tags = True

    def description_admin(self):
        return self.description and true_icon() or false_icon()
    description_admin.short_description = u'Свое описание'
    description_admin.allow_tags = True

    def save(self):
        if not self.description:
            self.description = self.tag.description
        super(TagProductBase, self).save()

    class Meta:
        verbose_name_plural = u'Продукт-Тег-Описание'
        abstract = True
