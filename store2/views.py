# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from bicycle.core.shortcuts import session_start
from bicycle.core.views import JsonResponseMixin
from bicycle.core.views import ResponseMixin
from bicycle.core.views import ToDoView


class CartError(Exception):
    pass


class CartMixin:

    def get(self, request, *args, **kwargs):
        raise NotImplementedError()

    def get_widget(self, request, *args, **kwargs):
        raise NotImplementedError()

    def post_add(self, request, *args, **kwargs):
        raise NotImplementedError()

    def post_change(self, request, *args, **kwargs):
        raise NotImplementedError()

    def post_clear(self, request, *args, **kwargs):
        raise NotImplementedError()

    def post_delete(self, request, *args, **kwargs):
        raise NotImplementedError()

    def post_one_click(self, request, *args, **kwargs):
        raise NotImplementedError()


class CartViewBase(CartMixin, ResponseMixin, JsonResponseMixin, ToDoView):
    model = None
    item_model = None
    order_model = None
    orderitem_model = None
    reverse_relation = 'cartitem_set'

    add_form = None
    change_form = None
    delete_form = None
    one_click_form = None

    template_name = 'cart/cart.html'
    widget_template = 'cart/widget.html'

    cart = None

    def _get_cart(self, request, *args, **kwargs):
        if self.cart is not None:
            return self.cart
        elif self.model is not None:
            try:
                self.cart = self.model.objects.get(session_key=session_start(request))
            except ObjectDoesNotExist:
                self.cart = self.model(session_key=session_start(request))
                try:
                    self.cart.full_clean()
                except ValidationError:
                    raise CartError('self.cart.full_clean() exception')
                self.cart.save()
            return self.cart
        else:
            raise CartError('model was not specified')

    def _cart_has_the_item(self, request, item):
        cart = self._get_cart(request)
        reverse_relation = getattr(cart, self.reverse_relation)
        return item in reverse_relation.all()

    def get(self, request, *args, **kwargs):
        c = {'object': self._get_cart(request)}
        return self.response(request, self.template_name, c)

    def get_widget(self, request, *args, **kwargs):
        c = {'object': self._get_cart(request)}
        return self.response(request, self.widget_template, c, False)
