# coding: UTF-8

from django import forms


class AddToCartMetaForm(forms.forms.DeclarativeFieldsMetaclass):

    def __new__(cls, name, bases, attrs):
        if attrs['PRODUCT_MODEL'] is not None:
            attrs['product'] = forms.ModelChoiceField(
                queryset=attrs['PRODUCT_MODEL'].objects.published())
        return super(AddToCartMetaForm, cls).__new__(cls, name, bases, attrs)


class AddToCartBaseForm(forms.Form):
    PRODUCT_MODEL = None

    def get_params(self, qty=1):
        return (self.cleaned_data['product'], 1)


class CartQtyChangeMetaForm(forms.forms.DeclarativeFieldsMetaclass):

    def __new__(cls, name, bases, attrs):
        if attrs['CART_ITEM_MODEL'] is not None:
            attrs['cart_item'] = forms.ModelChoiceField(
                queryset=attrs['CART_ITEM_MODEL'].objects.all())
        return super(CartQtyChangeMetaForm, cls).__new__(cls, name, bases, attrs)


class CartQtyChangeBaseForm(forms.Form):
    CART_ITEM_MODEL = None
    qty = forms.IntegerField()

    def clean_qty(self):
        if self.cleaned_data['qty'] <= 0:
            return 1
        else:
            return self.cleaned_data['qty']


class CartRowDeleteMetaForm(forms.forms.DeclarativeFieldsMetaclass):

    def __new__(cls, name, bases, attrs):
        if attrs['CART_ITEM_MODEL'] is not None:
            attrs['cart_item'] = forms.ModelChoiceField(
                queryset=attrs['CART_ITEM_MODEL'].objects.all())
        return super(CartRowDeleteMetaForm, cls).__new__(cls, name, bases, attrs)


class CartRowDeleteBaseForm(forms.Form):
    CART_ITEM_MODEL = None


class CheckoutBaseForm(forms.ModelForm):
    confirm = forms.BooleanField(required=True)

    class Meta(object):
        # model = ORDER_MODEL
        exclude = ['user', 'created', 'updated', 'status', 'oid', ]
        widgets = {
            'payment_method': forms.widgets.RadioSelect
        }


class OrderEditForme(forms.ModelForm):

    class Meta(object):
        # model = ORDER_MODEL
        fields = ('status', 'payment_method', 'user', 'first_name', 'last_name', 'email',
                  'phone', 'city', 'street', 'house', 'apartment', 'note',)


class OrderAddRowMeta(forms.forms.DeclarativeFieldsMetaclass):

    def __new__(cls, name, bases, attrs):
        if attrs['PRODUCT_MODEL'] is not None:
            attrs['product'] = forms.ModelChoiceField(
                queryset=attrs['PRODUCT_MODEL'].objects.published())
        if attrs['ORDER_MODEL'] is not None:
            attrs['order'] = forms.ModelChoiceField(
                queryset=attrs['ORDER_MODEL'].objects.filter(status=attrs['FILTER_STATUS']),
                widget=forms.HiddenInput)
        return super(OrderAddRowMeta, cls).__new__(cls, name, bases, attrs)


class OrderAddRow(forms.Form):
    ORDER_MODEL = None
    PRODUCT_MODEL = None
    FILTER_STATUS = ''
    qty = forms.IntegerField()


class OrderDeleteRowMeta(forms.forms.DeclarativeFieldsMetaclass):

    def __new__(cls, name, bases, attrs):
        if attrs['ORDER_ITEM_MODEL'] is not None:
            attrs['order_item'] = forms.ModelChoiceField(
                queryset=attrs['ORDER_ITEM_MODEL'].objects.all(),
                widget=forms.HiddenInput)
        return super(OrderDeleteRowMeta, cls).__new__(cls, name, bases, attrs)


class OrderDeleteRow(forms.Form):
    ORDER_ITEM_MODEL = None
    FILTER_STATUS = ''
