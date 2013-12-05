# coding: UTF-8

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.db import models
from django.db.models.query import EmptyQuerySet
from bicycle.djangomixins.shortcuts import session_start


def default_return(func):
    """
    Decorator, return 0 if self.cart_items is None
    """

    def _inner(self, *args, **kwargs):
        if self.cart_items is None:
            return 0
        return func(self, *args, **kwargs)
    return _inner


class CartBase(object):
    PRODUCT_MODEL = None
    CART_ITEM_MODEL = None
    ORDER_ITEM_MODEL = None

    cart_items = EmptyQuerySet()
    request = None
    user = None

    class NotListed(Exception):
        pass

    def __init__(self, request):
        assert isinstance(request, HttpRequest)
        if request.user.is_authenticated():
            self.cart_items = self.CART_ITEM_MODEL.objects.filter(user=request.user)
            self.user = request.user
        else:
            self.request = request
            if getattr(request.session, 'session_key', None) is not None:
                sk = request.session.session_key
                self.cart_items = self.CART_ITEM_MODEL.objects.filter(session_key=sk)

    @default_return
    def total_qty(self):
        total_qty = 0
        for item in self.cart_items:
            total_qty += item.qty
        return total_qty

    @default_return
    def total_price(self):
        total_price = 0
        for item in self.cart_items:
            total_price += item.total_price()
        return total_price

    @default_return
    def total_price_with_discount(self):
        total_price = 0
        for item in self.cart_items:
            total_price += item.total_price_with_discount()
        return total_price

    def get_items_set(self):
        return self.cart_items

    def get_item(self, product):
        assert isinstance(product, self.PRODUCT_MODEL)
        for item in self.cart_items:
            if item.product == product:
                return item
        return False

    def add_item(self, product, qty):
        assert isinstance(product, self.PRODUCT_MODEL)
        assert type(qty) is int
        item = self.get_item(product)
        if item:
            item.qty += qty
            item.full_clean()
            item.save()
        else:
            if self.user is not None:
                item = self.CART_ITEM_MODEL(user=self.user,
                                            product=product,
                                            qty=qty)
            else:
                item = self.CART_ITEM_MODEL(session_key=session_start(self.request),
                                            product=product,
                                            qty=qty)
            item.full_clean()
            item.save()

    def attach_items(self, user):
        for item in self.cart_items:
            item.user = user
            item.session_key = None
            item.full_clean()
            item.save()

    def listed(self, cart_item):
        if cart_item not in self.get_items_set():
            raise NotListed()

    def empty_the_cart(self):
        self.cart_items.delete()

    def checkout(self, order):
        for item in self.cart_items:
            initial = {
                'order': order,
                'title': item.product.title,
                'alias': item.product.alias,
                'retail_price': item.product.retail_price,
                'discount': item.product.discount,
                'qty': item.qty,
                'sku': item.product.sku,
            }
            self.ORDER_ITEM_MODEL.objects.create(**initial)
        self.empty_the_cart()
