# coding: UTF-8

import re

from django.forms.fields import CharField
from south.modelsinspector import add_introspection_rules


class PhoneField(CharField):
    def __init__(self, max_length=None, *args, **kwargs):
        super(PhoneField, self).__init__(max_length=11, *args, **kwargs)

    def to_python(self, value):
        value = re.sub('[^0-9]', '', value)
        return super(PhoneField, self).to_python(value)


class PassportField(CharField):
    def __init__(self, max_length=None, *args, **kwargs):
        super(PassportField, self).__init__(max_length=10, *args, **kwargs)

    def to_python(self, value):
        if value is not None:
            value = re.sub('[^0-9]', '', value)
        return super(PassportField, self).to_python(value)


add_introspection_rules([], ["^bicycle\.core\.models\.fields\.PhoneField"])
add_introspection_rules([], ["^bicycle\.core\.models\.fields\.PassportField"])
