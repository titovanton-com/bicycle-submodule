# -*- coding: utf-8 -*-

from django import template


register = template.Library()


def mod0(value, arg):
    if value % int(arg) == 0:
        return True
    else:
        return False


def mod(value, arg):
    return value % int(arg)


register.filter('mod', mod)
register.filter('mod0', mod0)
