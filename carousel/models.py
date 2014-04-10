# -*- coding: utf-8 -*-

from django.db import models
from bicycle.djangomixins.models import SlugMixin
from bicycle.djangomixins.models import ImageBase


class Carousel(SlugMixin):

    def img_count(self):
        return self.carouselimage_set.count()
    img_count.short_description = u'Число картинок'
    img_count.allow_tags = True

    def get_images(self):
        return self.carouselimage_set.all()

    class Meta(object):
        verbose_name_plural = u'Карусели'


class CarouselImage(ImageBase):
    carousel = models.ForeignKey(Carousel, verbose_name=u'Карусель')
    link = models.URLField(blank=True, null=True, verbose_name=u'Ссылка')

    class Meta:
        ordering = ['position', '-pk']
        verbose_name_plural = u'Изображения для Карусели'
