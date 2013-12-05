# coding: UTF-8

from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.core.context_processors import csrf
from bicycle.futuremessage.models import FutureMessage
from bicycle.djangomixins.views import ToDoView
from bicycle.djangomixins.views import RenderWithContextMixin
from bicycle.rest.views import JsonResponseMixin


class CartMixin(object):

    """
    Use it before ToDoMixin in base list
    """
    cart_class = None

    def dispatch(self, request, *args, **kwargs):
        self.cart = self.cart_class(request)
        return super(CartMixin, self).dispatch(request, *args, **kwargs)


class CartContextMixin(CartMixin):

    def get_context_data(self, **kwargs):
        kwargs['cart'] = self.cart
        return super(CartContextMixin, self).get_context_data(**kwargs)


class CartViewBase(CartContextMixin, RenderWithContextMixin, ToDoView):
    add_form = None
    qty_form = None
    delete_form = None
    widget_template = 'cart/widget.html'
    template_name = None

    def post_add(self, request, *args, **kwargs):
        form = self.add_form(request.POST)
        if form.is_valid():
            self.cart.add_item(*form.get_params())
        return redirect('/store/cart/')

    def post_qty(self, request, *args, **kwargs):
        form = self.qty_form(request.POST)
        if form.is_valid():
            cart_item = form.cleaned_data['cart_item']
            cart_item.qty = form.cleaned_data['qty']
            cart_item.save()
        return redirect('/store/cart/')

    def post_delete(self, request, *args, **kwargs):
        form = self.delete_form(request.POST)
        if form.is_valid():
            form.cleaned_data['cart_item'].delete()
        return redirect('/store/cart/')

    def post_clear(self, request, *args, **kwargs):
        self.cart.empty_the_cart()
        return redirect('/store/cart/')

    def get_cart_widget(self, request, *args, **kwargs):
        return self.response(request, self.widget_template, {}, False)

    def get(self, request, *args, **kwargs):
        return self.response(request, self.template_name, {})


class CheckoutViewBase(TemplateView):
    template_name = None
    checkout_forms = None
    checkout_success_title = u''
    checkout_success_text = u''

    def dispatch(self, request, *args, **kwargs):
        if not self.cart.get_items_set():
            return redirect('/')
        if request.user.is_authenticated():
            self.user = request.user
        else:
            self.user = None
        return super(CheckoutBase, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.user:
            profile = user.get_profile()
            initial = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': profile.unique_email,
            }
        else:
            profile = None
            initial = {}

        # context
        kwargs['form'] = self.checkout_forms(instance=profile, initial=initial)
        kwargs['breadcrumbs'] = [('/', u'Главная'), ('/store/cart/', u'Корзина'),
                                 'Оформление заказа', ]
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.checkout_forms(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.save()
            self.cart.checkout(order)
            msg = {
                'user': user,
                'session_key': user is None and request.session.session_key or None,
                'mtype': 'success',
                'title': self.checkout_success_title,
                'text': self.checkout_success_text,
            }
            FutureMessage.objects.create(**msg)
            if user is None:
                return redirect('/')
            return redirect(order.get_url())

        # context
        kwargs['form'] = form
        kwargs['breadcrumbs'] = [('/', u'Главная'), ('/store/cart/', u'Корзина'),
                                 'Оформление заказа', ]
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class OrderViewBase(ToDoView):
    model = None
    item_model = None
    template_name = ''
    edit_template = ''
    edit_permissions = ''
    edit_form = None
    add_form = None
    delete_form = None

    def get(request, oid):
        try:
            order = self.model.objects.get(oid=oid)
        except self.model.DoesNotExist:
            return redirect('/')
        context = {
            'order': order,
            'add_row_form': self.add_form(initial={'order': order, 'qty': 1}),
        }
        context.update(self.hook_order(request))
        if request.user.has_perm(edit_permissions):
            if request.method == 'POST':
                form = self.edit_form(data=request.POST, instance=order)
                if form.is_valid():
                    form.save()
                    return redirect(order.get_url())
            else:
                form = self.edit_form(instance=order)
            context['order_form'] = form
            return render(request, self.edit_template, context)
        return render(request, self.template_name, context)

    def post_add(request):
        form = self.add_form(request.POST)
        if form.is_valid():
            order = form.cleaned_data['order']
            product = form.cleaned_data['product']
            qty = form.cleaned_data['qty']
            order.add_item(product, qty)
            return redirect(order.get_url())
        return redirect('/')

    def post_delete(request):
        form = self.delete_form(request.POST)
        if form.is_valid():
            order = form.cleaned_data['order_item'].order
            form.cleaned_data['order_item'].delete()
            return redirect(order.get_url())
        return redirect('/')

    def hook_order(request):
        return {}


class RestCartViewBase(CartContextMixin, JsonResponseMixin, ToDoView):
    cart_item_model = None
    cart_item_resource = None
    product_model = None

    def put_item(self, request, *args, **kwargs):
        pk = int(kwargs.get('pk'))
        qty = int(kwargs.get('qty'))
        result = 'OK'
        try:
            cart_item = self.cart_item_model.objects.get(pk=pk)
            self.cart.listed(cart_item)
        except (self.cart_item_model.DoesNotExist, self.cart.NotListed):
            result = 'FAIL'
        else:
            cart_item.qty = qty
            cart_item.save()
        return self.response(result)

    def put_product(self, request, *args, **kwargs):
        pk = int(kwargs.get('pk'))
        qty = int(kwargs.get('qty'))
        result = 'OK'
        try:
            product = self.product_model.objects.get(pk=pk)
        except self.product_model.DoesNotExist:
            result = 'FAIL'
        else:
            self.cart.add_item(product, qty)
        return self.response(result)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        result = 'OK'
        if pk is not None:
            try:
                cart_item = self.cart_item_model.objects.get(pk=pk)
                self.cart.listed(cart_item)
            except (self.cart_item_model.DoesNotExist, self.cart.NotListed):
                result = 'FAIL'
            else:
                cart_item.delete()
        else:
            self.cart.empty_the_cart()
        return self.response(result)

    def get(self, request, *args, **kwargs):
        res = self.cart_item_resource()
        bundles = []
        items_set = self.cart.get_items_set()

        # make bundles set from queryset
        for obj in items_set:
            bundle = res.build_bundle(obj=obj, request=request)
            bundles.append(res.full_dehydrate(bundle, for_list=True))

        # make meta
        data = {}
        data['meta'] = {}
        data['meta']['total_qty'] = self.cart.total_qty()
        data['meta']['total_price'] = self.cart.total_price()
        data['meta']['total_price_with_discount'] = self.cart.total_price_with_discount()
        data['meta']['csrf_header_name'] = 'X-CSRFToken'
        data['meta']['csrf_header_value'] = csrf(request)['csrf_token']
        data['objects'] = bundles
        return self.response(res.serialize(None, data, "application/json"), True)
