# coding: UTF-8

from django import template

register = template.Library()


@register.filter('get')
def get(deect, key):
    """
    Return value of dict if it does exists, else return empty string
    """
    return deect.get(key, '')
