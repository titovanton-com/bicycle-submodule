# -*- coding: utf-8 -*-

from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

from models import Carousel
from models import CarouselImage


class CarouselImageInline(AdminImageMixin, admin.StackedInline):
    model = CarouselImage
    fk_name = 'carousel'
    sortable_field_name = 'position'
    extra = 0


class CarouselAdmin(AdminImageMixin, admin.ModelAdmin):
    inlines = [CarouselImageInline, ]
    list_display = ('title', 'img_count',)


admin.site.register(Carousel, CarouselAdmin)
# admin.site.register(CarouselImage)
