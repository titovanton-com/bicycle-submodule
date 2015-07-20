# coding: UTF-8

import re

from django import template
from django.template.base import FilterExpression


register = template.Library()


class AddParameter(template.Node):

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        request = template.resolve_variable('request', context)
        get = request.GET.copy()
        for key in self.kwargs:
            value = self.kwargs[key]
            get[key] = isinstance(value, FilterExpression) \
                and value.resolve(context, True) \
                or value
        return '?%s' % get.urlencode()


def extract_string(string, parser, tag_name):
    m1 = re.search(r'^"([a-zA-Z0-9_]+?)"="([a-zA-Z0-9_]+?)"$', string)
    m2 = re.search(r'^"([a-zA-Z0-9_]+?)"=([a-zA-Z0-9._]+?)$', string)
    if m1:
        param, value = m1.groups()
        return (param, value)
    elif m2:
        param, var_name = m2.groups()
        var = parser.compile_filter(var_name)
        return (param, var)
    else:
        msg = '%r tag had invalid arguments: %s' % (tag_name, string)
        raise template.TemplateSyntaxError(msg)


@register.tag
def addurlparameter(parser, token):
    """Add GET parameter to the URL

    Example usage in html template:
        <a href="{% addurlparameter "p"="1" %}">blabla bla</a>
        <a href="{% addurlparameter "hey"=variable "param"="1" %}">omnomn omn</a>
    """

    try:
        bits = token.contents.split(' ')
        tag_name = bits.pop(0)
    except ValueError:
        msg = '%r tag requires arguments' % token.contents[0]
        raise template.TemplateSyntaxError(msg)
    kwargs = dict(extract_string(string, parser, tag_name) for string in bits)
    return AddParameter(kwargs)


class RemoveParameter(template.Node):

    def __init__(self, args):
        self.args = args

    def render(self, context):
        request = template.resolve_variable('request', context)
        get = request.GET.copy()
        for key in self.args:
            try:
                get.pop(key)
            except KeyError:
                pass
        return '?%s' % get.urlencode()


@register.tag
def removeurlparameter(parser, token):
    """Remove GET parameter by name

    Example usage in html template:
        <a href="{% removeurlparameter "foo" "bar" %}">blabla bla</a>
    """

    try:
        bits = token.contents.split(' ')
        tag_name = bits.pop(0)
    except ValueError:
        msg = '%r tag requires arguments' % token.contents[0]
        raise template.TemplateSyntaxError(msg)
    args = [string[1:-1] for string in bits]
    return RemoveParameter(args)
