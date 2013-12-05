# coding: UTF-8

import re

from django.forms.fields import CharField


class PhoneField(CharField):
    def __init__(self, max_length=None, *args, **kwargs):
        super(PhoneField, self).__init__(max_length=11, *args, **kwargs)

    def to_python(self, value):
        value = re.sub('[^0-9]', '', value)
        return super(PhoneField, self).to_python(value)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^bicycle\.djangomixins\.models\.fields\.PhoneField"])