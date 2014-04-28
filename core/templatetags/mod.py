# -*- coding: utf-8 -*-

from django import template


register = template.Library()


def mod(value, arg):
    if value % int(arg) == 0:
        return True
    else:
        return False


register.filter('mod', mod)
