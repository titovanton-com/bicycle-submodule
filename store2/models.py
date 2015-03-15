# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from bicycle.core.models import CoverModel
from bicycle.core.models import TitleModel


class OrderMixin(object):

    def total_discounted(self, *args, **kwargs):
        raise NotImplementedError()

    def total_price(self, *args, **kwargs):
        raise NotImplementedError()

    def total_qty(self, *args, **kwargs):
        raise NotImplementedError()

    def total_saving(self, *args, **kwargs):
        raise NotImplementedError()


class CartMixin(OrderMixin):

    def make_an_order(self, *args, **kwargs):
        raise NotImplementedError()


class CartItemMixin(object):

    def get_discounted(self):
        raise NotImplementedError()

    def get_price(self):
        raise NotImplementedError()

    def get_qty(self):
        raise NotImplementedError()

    def get_saving(self, *args, **kwargs):
        raise NotImplementedError()

    def get_total_discounted(self, *args, **kwargs):
        raise NotImplementedError()

    def get_total_price(self, *args, **kwargs):
        raise NotImplementedError()

    def get_total_saving(self, *args, **kwargs):
        raise NotImplementedError()


class CartModelBase(CartMixin, models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True)

    class Meta(object):
        abstract = True


class CartItemModelBase(CartItemMixin, models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    qty = models.PositiveIntegerField(default=1)

    class Meta(object):
        abstract = True


class OrderModelBase(OrderMixin, models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True)

    class Meta(object):
        abstract = True


class OrderItemModelBase(CartItemMixin, TitleModel, CoverModel):
    link = models.TextField()
    price = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    qty = models.PositiveIntegerField()

    class Meta(object):
        abstract = True
