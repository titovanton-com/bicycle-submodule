# coding: UTF-8

from django.conf.urls import patterns
from django.conf.urls import url

from views import CartViewBase
from views import CheckoutViewBase
from views import OrderViewBase


urlpatterns = patterns('',
    url(r'^checkout/$', CheckoutViewBase.as_view()),
    url(r'^cart/(?P<todo>\w+?)/$', CartViewBase.as_view()),
    url(r'^order/(?P<oid>[a-zA-Z0-9]+)/$', OrderViewBase.as_view(todo='page')),
    url(r'^order/(?P<todo>\w+?)/$', OrderViewBase.as_view()),
)


def store_urlpatterns(CartView, CheckoutView, OrderView):
    return patterns('',
        url(r'^checkout/$', CheckoutView.as_view()),
        url(r'^cart/$', CartView.as_view()),
        url(r'^cart/(?P<todo>\w+?)/$', CartView.as_view()),
        url(r'^order/(?P<oid>[a-zA-Z0-9]+)/$', OrderView.as_view(todo='page')),
        url(r'^order/(?P<todo>\w+?)/$', OrderView.as_view()),
    )


def rest_store_urlpatterns(CartView, CheckoutView, OrderView):
    return patterns('',
        # GET and DELETE all cart items
        url(r'cart/$', CartView.as_view()),
        # DELETE one cart item
        url(r'cart/(?P<pk>[0-9]+)/$', CartView.as_view()),
        # PUT item(cart_item.pk, qty) or product(product.pk, qty)
        url(r'cart/(?P<todo>\w+)/(?P<pk>\d+)/(?P<qty>\d+)/$', CartView.as_view()),
        url(r'checkout/$', CheckoutView.as_view()),
        url(r'order/(?P<oid>[a-zA-Z0-9]+)/$', OrderView.as_view(todo='page')),
        url(r'order/(?P<todo>\w+)/$', OrderView.as_view()),
    )