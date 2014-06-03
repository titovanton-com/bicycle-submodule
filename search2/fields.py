# -*- coding: utf-8 -*-


class BaseField(object):

    def __init__(self, **kwargs):
        kwargs['type'] = self.mapping()
        kwargs['analyzer'] = 'my_analyzer'
        self.data = kwargs

    def mapping(self):
        return 'string'


class StringField(BaseField):
    pass


class IntegerField(BaseField):

    def mapping(self):
        return 'integer'


class LongField(BaseField):

    def mapping(self):
        return 'long'


class FloatField(BaseField):

    def mapping(self):
        return 'float'


class DoubleField(BaseField):

    def mapping(self):
        return 'double'


class BooleanField(BaseField):

    def mapping(self):
        return 'boolean'


class NullField(BaseField):

    def mapping(self):
        return 'null'
