# coding: UTF-8

import re

from django.db.models import CharField

from bicycle.djangomixins import forms


class PhoneField(CharField):
    def __init__(self, max_length=None, *args, **kwargs):
        super(PhoneField, self).__init__(max_length=11, *args, **kwargs)

    def formfield(self, form_class=None, **kwargs):
        return super(PhoneField, self).formfield(form_class=forms.PhoneField, **kwargs)

    def to_python(self, value):
        value = re.sub('[^0-9]', '', value)
        return super(PhoneField, self).to_python(value)

