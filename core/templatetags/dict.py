# coding: UTF-8

from django import template

register = template.Library()


@register.filter
def get(deect, key):
    """
    Return value of dict if it does exists, else return empty string

    Usage:
        {{ dict|get:"key" }}

    With default value:
        {{ dict|get:"key"|default:"value" }}
    """
    return deect.get(key, '')
