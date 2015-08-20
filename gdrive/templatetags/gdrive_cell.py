# coding: UTF-8

import re

from django import template
from django.utils.encoding import force_unicode

register = template.Library()


@register.filter
def row(value):
    orig = force_unicode(value)
    new = re.sub("^R(\d+)C(\d+)$", '\g<1>', orig)
    return new


@register.filter
def col(value):
    orig = force_unicode(value)
    new = re.sub("^R(\d+)C(\d+)$", '\g<2>', orig)
    return new


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')
