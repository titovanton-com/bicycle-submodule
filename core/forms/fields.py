# -*- coding: utf-8 -*-

import re

import dateutil.parser

from django.forms.fields import CharField
from django.forms.fields import DateTimeField
from django.utils.encoding import force_str


class PhoneField(CharField):

    def __init__(self, max_length=None, *args, **kwargs):
        super(PhoneField, self).__init__(max_length=11, *args, **kwargs)

    def to_python(self, value):
        if value is not None:
            value = re.sub('[^0-9]', '', value)
        return super(PhoneField, self).to_python(value)


class PassportField(CharField):

    def __init__(self, max_length=None, *args, **kwargs):
        super(PassportField, self).__init__(max_length=10, *args, **kwargs)

    def to_python(self, value):
        if value is not None:
            value = re.sub('[^0-9]', '', value)
        return super(PassportField, self).to_python(value)


class SmartDateTimeField(DateTimeField):

    """
        It does not depend on input_formats parameter,
        because strptime does not need it while parsing.
    """

    def strptime(self, value, format):
        return dateutil.parser.parse(force_str(value))
