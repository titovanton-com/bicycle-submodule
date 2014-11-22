# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from bicycle.core.shortcuts import session_start
from bicycle.core.views import JsonResponseMixin
from bicycle.core.views import ResponseMixin
from bicycle.core.views import ToDoView


class CartMixin(object):

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
    reverse_relation = 'cartitem_set'

    add_form = None
    change_form = None
    delete_form = None
    one_click_form = None

    template_name = 'cart/cart.html'
    widget_template = 'cart/widget.html'

    def get(self, request, *args, **kwargs):
        if self.model is not None:
            try:
                obj = self.model.objects.get(session_key=session_start(request))
            except ObjectDoesNotExist:
                obj = self.model(session_key=session_start(request))
            c = {'object': obj}
        return self.response(request, self.template_name, c)

    def get_widget(self, request, *args, **kwargs):
        if self.model is not None:
            try:
                obj = self.model.objects.get(session_key=session_start(request))
            except ObjectDoesNotExist:
                obj = self.model(session_key=session_start(request))
            c = {'object': obj}
        return self.response(request, self.widget_template, c, False)
