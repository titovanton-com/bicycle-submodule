# -*- coding: utf-8 -*-

from django.db import models
from bicycle.core.models import SlugModel
from bicycle.core.models import ImageBase


class CarouselBase(SlugModel):

    def img_count(self):
        return self.carouselimage_set.count()
    img_count.short_description = u'Число картинок'
    img_count.allow_tags = True

    def get_images(self):
        return self.carouselimage_set.all()

    class Meta:
        abstract = True


class Carousel(CarouselBase):

    class Meta:
        verbose_name_plural = u'Карусель'


class CarouselImageBase(ImageBase):
    link = models.URLField(blank=True, null=True, verbose_name=u'Ссылка')

    class Meta:
        abstract = True


class CarouselImage(CarouselImageBase):
    carousel = models.ForeignKey(Carousel, verbose_name=u'Карусель')

    class Meta:
        ordering = ['position', '-pk']
        verbose_name_plural = u'Изображения для Карусели'
