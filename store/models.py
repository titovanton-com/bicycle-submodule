# coding: UTF-8

from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings
from bicycle.djangomixins.models import PhoneField
from bicycle.djangomixins.models import StandartQuerySet
from bicycle.djangomixins.models import StandartManager
from bicycle.djangomixins.models import ChronologyMixin
from bicycle.djangomixins.models import AliasRequiredMixin
from bicycle.djangomixins.models import SeoMixin
from bicycle.djangomixins.models import ChronologyMixin
from bicycle.djangomixins.models import TitleMixin
from bicycle.djangomixins.utilites import md5_random_string


class BillingMixin(models.Model):
    phone = PhoneField(verbose_name=u'Телефон')
    city = models.CharField(max_length=100, verbose_name=u'Город')
    street = models.CharField(max_length=100, verbose_name=u'Улица')
    house = models.CharField(max_length=10, verbose_name=u'Дом')
    apartment = models.CharField(max_length=10, verbose_name=u'Квартира')

    class Meta(object):
        abstract = True


class TodaysQuerySetMixin(object):

    def get_todays_products(self, **kwargs):
        return self.get_published(todays_product=True, **kwargs)

    def todays_products(self, **kwargs):
        return self.published(todays_product=True, **kwargs)


class BestsellerQuerySetMixin(object):

    def get_best_sellers(self, **kwargs):
        return self.get_published(best_seller=True, **kwargs)

    def best_sellers(self, **kwargs):
        return self.published(best_seller=True, **kwargs)


class OnSaleQuerySetMixin(object):

    def get_on_sale(self, **kwargs):
        return self.get_published(discount__gt=0, **kwargs)

    def on_sale(self, **kwargs):
        return self.published(discount__gt=0, **kwargs)


class NewestQuerySetMixin(object):

    def get_newest(self, **kwargs):
        d = now() - timedelta(days=settings.STORE_GOODS_FRESHNESS)
        return self.get_published(created__gte=d, **kwargs)

    def newest(self, **kwargs):
        d = now() - timedelta(days=settings.STORE_GOODS_FRESHNESS)
        return self.published(created__gte=d, **kwargs)


class ProductQuerySet(TodaysQuerySetMixin, BestsellerQuerySetMixin, OnSaleQuerySetMixin,
                      NewestQuerySetMixin, StandartQuerySet):
    pass


class ProductManager(StandartManager):

    def get_query_set(self):
        return ProductQuerySet(self.model, using=self._db)

    def get_todays_products(self, **kwargs):
        return self.get_query_set().get_todays_products(**kwargs)

    def todays_products(self, **kwargs):
        return self.get_query_set().todays_products(**kwargs)

    def get_best_sellers(self, **kwargs):
        return self.get_query_set().get_best_sellers(**kwargs)

    def best_sellers(self, **kwargs):
        return self.get_query_set().best_sellers(**kwargs)

    def get_on_sale(self, **kwargs):
        return self.get_query_set().get_on_sale(**kwargs)

    def on_sale(self, **kwargs):
        return self.get_query_set().on_sale(**kwargs)

    def get_newest(self, **kwargs):
        return self.get_query_set().get_newest(**kwargs)

    def newest(self, **kwargs):
        return self.get_query_set().newest(**kwargs)


def product_get_price(self):
    return self.retail_price


def product_get_price_with_discount(self):
    return self.retail_price * (1 - self.discount / 100)


class ProductMeta(models.base.ModelBase):

    def __new__(cls, name, bases, attrs):
        new = super(ProductMeta, cls).__new__(cls, name, bases, attrs)
        new.add_to_class('sku', models.CharField(max_length=60, unique=True,
                                                 verbose_name=u'Артикул',
                                                 blank=new.SKU_TEXT_BLANK))
        new.add_to_class('published', models.BooleanField(verbose_name=u'Опубликован',
                                                          default=new.PUBLISHED_DEFAULT))
        if new.SELL_TEXT_IS_NEEDED:
            new.add_to_class('sell_text', models.CharField(max_length=260,
                                                           verbose_name=u'Sell текст',
                                                           blank=new.SELL_TEXT_BLANK))
        if new.COST_IS_NEEDED:
            new.add_to_class('cost', models.FloatField(verbose_name=u'Себестоимость', default=0))
        if new.RETAIL_PRICE_IS_NEEDED:
            new.add_to_class('retail_price', models.FloatField(verbose_name=u'Розничная цена',
                                                               default=0))
            new.get_price = product_get_price
        if new.DISCOUNT_IS_NEEDED:
            new.add_to_class('discount', models.IntegerField(verbose_name=u'Скидка', default=0))
            if new.RETAIL_PRICE_IS_NEEDED:
                new.get_price_with_discount = product_get_price_with_discount
        return new


class ProductBase(ChronologyMixin, AliasRequiredMixin, SeoMixin):

    # flags
    PUBLISHED_DEFAULT = True
    SKU_TEXT_BLANK = False
    SELL_TEXT_BLANK = False

    # needed
    SELL_TEXT_IS_NEEDED = True
    COST_IS_NEEDED = True
    RETAIL_PRICE_IS_NEEDED = True
    DISCOUNT_IS_NEEDED = True

    order_by = models.IntegerField(null=True, blank=True, verbose_name=u'Порядок в списке')
    description = models.TextField(verbose_name=u'Описание')
    best_seller = models.BooleanField(verbose_name=u'Самое популярное')
    todays_product = models.BooleanField(verbose_name=u'Продукт дня')

    objects = ProductManager()

    def get_url_by_sku(self):
        return u'/%s/sku/%s/' % (self.__class__.__name__.lower(), self.sku)

    def get_url(self):
        return self.get_url_with_app()

    class Meta(object):
        abstract = True
        verbose_name_plural = u'Товары'


class CartItemMeta(models.base.ModelBase):

    def __new__(cls, name, bases, attrs):
        new = super(CartItemMeta, cls).__new__(cls, name, bases, attrs)
        new.add_to_class('product', models.ForeignKey(new.PRODUCT_MODEL))
        new.Meta.unique_together = ('session_key', 'product',)
        return new


class CartItemBase(models.Model):
    PRODUCT_MODEL = None

    session_key = models.CharField(max_length=40, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    qty = models.IntegerField()

    def clean(self):
        if self.session_key is None and self.user is None or\
           self.session_key is not None and self.user is not None:
            raise models.ValidationError('You should set only one of two fields:'
                                         ' session_key or user')

    def total_price(self):
        return self.product.get_price() * self.qty

    def total_price_with_discount(self):
        return self.product.get_price_with_discount() * self.qty

    class Meta(object):
        abstract = True
        ordering = ['-pk']


class OrderMeta(models.base.ModelBase):

    def __new__(cls, name, bases, attrs):
        new = super(OrderMeta, cls).__new__(cls, name, bases, attrs)
        new.add_to_class('status', models.CharField(max_length=60, choices=new.STATUS_CHOICES,
                                                    verbose_name=u'Статус заказа',
                                                    default=u'In the process'))
        new.add_to_class('payment_method', models.CharField(max_length=60,
                                                            choices=new.PAYMENT_METHOD_CHOICES,
                                                            verbose_name=u'Способ оплаты',
                                                            default=u'cash on delivery'))
        return new


class OrderBase(ChronologyMixin, BillingMixin):

    STATUS_CHOICES = (
        (u'In the process', u'В процессе'),
        (u'Confirmed', u'Подтвержден'),
        (u'Completed', u'Выполнен'),
        (u'Canseled', u'Отменен'),
    )
    PAYMENT_METHOD_CHOICES = (
        (u'cash on delivery', u'Наличными при получении'),
        (u'by card on delivery', u'Пластиковой картой при получении'),
        (u'cash on pickup', u'Наличными, самовывоз'),
        (u'by card on pickup', u'Пластиковой картой, самовывоз'),
        (u'online', u'Онлайн оплата'),
        (u'credit', u'Оплата в кредит'),
    )

    first_name = models.CharField(u'Имя', max_length=30)
    last_name = models.CharField(u'Фамилия', max_length=30)
    email = models.EmailField(verbose_name=u'Email')
    note = models.TextField(verbose_name=u'Пожелания и дополнения', blank=True, null=True)
    oid = models.CharField(max_length=32, verbose_name=u'Номер заказа')
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Пользователь')

    def link_admin(self):
        return u'<a href="/store/order/%s/">Просмотр и редактирование</a>' % self.oid
    link_admin.short_description = 'link_admin'
    link_admin.allow_tags = True

    def user_admin(self):
        return '%s %s' % (self.first_name, self.last_name)
    user_admin.short_description = 'user_admin'
    user_admin.allow_tags = True

    def total(self):
        return sum((item.sub_total() for item in self.orderitem_set.all()))

    def total_qty(self):
        return sum((item.qty for item in self.orderitem_set.all()))

    def get_status(self):
        for t in self.STATUS_CHOICES:
            if t[0] == self.status:
                return t[1]
    get_status.short_description = 'get_status'
    get_status.allow_tags = True

    def get_payment_method(self):
        for t in self.PAYMENT_METHOD_CHOICES:
            if t[0] == self.payment_method:
                return t[1]
    get_payment_method.short_description = 'get_payment_method'
    get_payment_method.allow_tags = True

    def get_oid(self):
        return self.oid[:6]

    def get_url(self):
        return u'/store/order/%s/' % self.oid

    def add_item(self, product, qty):
        assert isinstance(product, ProductBase)
        items = OrderItem.objects.filter(order=order)
        for i in items:
            if i.alias == product.alias:
                i.qty += qty
                i.save()
                return True
        initial = {
            'title': product.title,
            'qty': qty,
            'sku': product.sku,
            'alias': product.alias,
            'retail_price': product.retail_price,
            'discount': product.discount,
            'order': order,
        }
        i = OrderItem.objects.create(**initial)
        return True

    def save(self):
        if not self.id:
            self.oid = md5_random_string().upper()
        super(OrderBase, self).save()

    def __unicode__(self):
        return u'Order object with oid: %s' % self.oid

    class Meta(object):
        abstract = True
        verbose_name_plural = u'Заказы'


class OrderItemMeta(models.base.ModelBase):

    def __new__(cls, name, bases, attrs):
        new = super(OrderItemMeta, cls).__new__(cls, name, bases, attrs)
        new.add_to_class('order', models.ForeignKey(new.ORDER_MODEL))
        new.Meta.unique_together = ('order', 'alias',)
        if new.SKU_NEEDED:
            new.add_to_class('sku', models.CharField(max_length=60, verbose_name=u'Артикул'))
        if new.RETAIL_PRICE_NEEDED:
            new.add_to_class('retail_price', models.FloatField(verbose_name=u'Розничная цена'))
        if new.DISCOUNT_NEEDED:
            new.add_to_class('discount', models.IntegerField(verbose_name=u'Скидка',
                                                             blank=True, null=True))
        return new


class OrderItemBase(TitleMixin):

    """
        U should name ur subclass as OrderItem, or OrderBase.add_item will not work
    """

    ORDER_MODEL = None
    PRODUCT_MODEL = None
    SKU_NEEDED = True
    RETAIL_PRICE_NEEDED = True
    DISCOUNT_NEEDED = True

    qty = models.IntegerField(verbose_name=u'Количество')
    alias = models.CharField(max_length=120, blank=True, verbose_name=u'Название латиницей')

    def price_with_discount(self):
        if self.discount:
            d = 1 - self.discount / 100.0
            return self.retail_price * d
        else:
            return self.retail_price

    def total_price_with_discount(self):
        return self.price_with_discount() * self.qty

    def get_url(self):
        try:
            product = PRODUCT_MODEL.objects.get_published(alias=self.alias)
            return product.get_url()
        except PRODUCT_MODEL.DoesNotExist:
            return False

    class Meta(object):
        abstract = True
        ordering = ['-pk']
        verbose_name_plural = u'Строки заказа'
