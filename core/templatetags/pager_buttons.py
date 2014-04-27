# coding: UTF-8

import re

from django import template
from django.core.paginator import Page

register = template.Library()


def do_page_list(page, quantity):
    if page.paginator.num_pages == 1:
        return None

    page_buttons = [n for n in \
                    range(page.number - quantity, page.number + quantity + 1) \
                    if n >= 1 and n <= page.paginator.num_pages]

    amount = quantity*2 + 2
    amount = amount > page.paginator.num_pages and page.paginator.num_pages
    while page_buttons[0] == 1 and len(page_buttons) < amount:
        if page_buttons[-1] + 1 <= page.paginator.num_pages:
            page_buttons.append(page_buttons[-1] + 1)

    while page_buttons[-1] == page.paginator.num_pages and len(page_buttons) < amount:
        if page_buttons[0] - 1 >= 1:
            page_buttons = [page_buttons[0] - 1] + page_buttons

    if page_buttons[0] > 2:
        page_buttons[0] = '...'
    if page_buttons[0] == '...' or page_buttons[0] > 1:
        page_buttons = [1] + page_buttons

    if page_buttons[-1] < page.paginator.num_pages - 1:
        page_buttons[-1] = '...'
    if page_buttons[-1] == '...' or page_buttons[-1] < page.paginator.num_pages:
        page_buttons.append(page.paginator.num_pages)

    return page_buttons

class PagerNode(template.Node):
    def __init__(self, nodelist, page, quantity, var_name):
        self.nodelist = nodelist
        self.page = page
        self.quantity = quantity
        self.var_name = var_name

    def render(self, context):
        page = self.page.resolve(context, True)
        assert isinstance(page, Page)

        context[self.var_name] = do_page_list(page, self.quantity)
        output = self.nodelist.render(context)
        return output


@register.tag
def pager(parser, token):
    """ Generate list of pager buttons

        Dependence on Paginator from django.core.paginator.
        See documentation: https://docs.djangoproject.com/en/1.4/topics/pagination/
        Example:
            {% pager page "3" as p %}
                ...
            {% endpager %}
        Where page is Page from django.core.paginator,
        3 is number of buttons attached to the left and right of current page button
        p is list of numbers and ellipsis with length <= 3*2 + 1 + 2, when number of buttons eq 3,
        for example:
            [1, '...', 5, 6, 7, 8, 9, '...', 50] # 7 - current page
    """

    nodelist = parser.parse(('endpager',))
    parser.delete_first_token()

    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        msg = '%r tag requires arguments' % token.contents[0]
        raise template.TemplateSyntaxError(msg)

    m = re.search(r'^([a-zA-Z0-9_.]+?) "(\d+?)" as ([a-zA-Z0-9_]+?)$', arg)
    if m:
        page_name, quantity, var_name = m.groups()
        page = parser.compile_filter(page_name)
    else:
        msg = '%r tag had invalid arguments' % tag_name
        raise template.TemplateSyntaxError(msg)

    return PagerNode(nodelist, page, int(quantity), var_name)
