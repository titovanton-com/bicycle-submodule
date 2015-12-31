# coding: UTF-8

import re

from django import template
from django.core.paginator import Page

register = template.Library()


def make_buttons_list(page_num, pages_total, buttons_total):

    if pages_total <= 1:
        return []

    if not buttons_total % 2:
        buttons_total += 1

    if buttons_total < 9:
        buttons_total = 9

    if page_num < 1:
        page_num = 1
    elif page_num > pages_total:
        page_num = pages_total

    buttons = [page_num]

    for i in range(1, buttons_total / 2 + 1):

        # to the left side
        if buttons[0] - 1 >= 1:
            buttons = [buttons[0] - 1] + buttons
        elif buttons[-1] + 1 <= pages_total:
            buttons = buttons + [buttons[-1] + 1]

        # to the right side
        if buttons[-1] + 1 <= pages_total:
            buttons = buttons + [buttons[-1] + 1]
        elif buttons[0] - 1 >= 1:
            buttons = [buttons[0] - 1] + buttons

    delta = pages_total - len(buttons)
    last = buttons[-1]
    first = buttons[0]

    if pages_total < buttons_total - 1:

        if page_num == 1:
            buttons = buttons + ['>']
        elif page_num < pages_total:
            buttons = ['<'] + buttons + ['>']
        else:
            buttons = ['<'] + buttons

    elif pages_total == buttons_total - 1:

        if page_num == 1:
            buttons = buttons + ['>']
        elif page_num < buttons_total / 2 + 1:
            buttons = ['<'] + buttons[:-3] + ['...', pages_total, '>']
        elif page_num >= buttons_total / 2 + 1 and page_num < pages_total:
            buttons = ['<', 1, '...'] + buttons[3:] + ['>']
        else:
            buttons = ['<', 1, '...'] + buttons[2:]

    else:

        if page_num == 1:
            buttons = buttons[:-3] + ['...', pages_total, '>']
        elif page_num < buttons_total / 2 + 1:
            buttons = ['<'] + buttons[:-4] + ['...', pages_total, '>']
        elif page_num < pages_total - 3:
            buttons = ['<', 1, '...'] + buttons[3:-3] + ['...', pages_total, '>']
        elif page_num < pages_total:
            buttons = ['<', 1, '...'] + buttons[4:] + ['>']
        else:
            buttons = ['<', 1, '...'] + buttons[3:]

    return buttons


class PagerNode(template.Node):

    def __init__(self, nodelist, page, buttons_total, var_name):
        self.nodelist = nodelist
        self.page = page
        self.buttons_total = buttons_total
        self.var_name = var_name

    def render(self, context):
        page = self.page.resolve(context, True)
        assert isinstance(page, Page)

        context[self.var_name] = make_buttons_list(
            page.number, page.paginator.num_pages, self.buttons_total)
        output = self.nodelist.render(context)
        return output


@register.tag
def pagerbuttons(parser, token):
    """ Generates list of pager buttons

        Dependences on Paginator from django.core.paginator.
        See documentation: https://docs.djangoproject.com/en/1.4/topics/pagination/

        Usage:

            {% pagerbuttons page "9" as buttons_list %}
                <nav class="pager-buttons">
                    {% for b in buttons_list %}
                        {% if b == '...' %}
                            <span>{{ b }}</span>
                        {% elif b == '<' %}
                            <a href="?stranitsa={{ page.previous_page_number }}">{{ b }}</a>
                        {% elif b == '>' %}
                            <a href="?stranitsa={{ page.next_page_number }}">{{ b }}</a>
                        {% elif b == page.number %}
                            <span class="current-page">{{ b }}</span>
                        {% else %}
                            <a href="?stranitsa={{ b }}">{{ b }}</a>
                        {% endif %}
                    {% endfor %}
                </nav>
            {% endpagerbuttons %}

        Where page is an instance of django.core.paginator.Page,
        and the second parameter is the number of buttons,
        which must be greater than or equal 9.
        If it is less then 9, then it will become 9 anyway.
        It also must be odd number, else it will be incremented by 1.

        Output example, where pages total is 40 and number of buttons is 12:

            ['<', 1, 2, 3, 4, 5, 6, 7, 8, 9, '...', 40, '>'] # current page is 2
            ['<', 1, '...', 17, 18, 19, 20, 21, 22, 23, '...', 40, '>'] # current page is 20
    """

    nodelist = parser.parse(('endpagerbuttons',))
    parser.delete_first_token()

    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        msg = '%r tag requires arguments' % token.contents[0]
        raise template.TemplateSyntaxError(msg)

    m = re.search(r'^([a-zA-Z0-9_.]+?) "(\d+?)" as ([a-zA-Z0-9_]+?)$', arg)
    if m:
        page_name, buttons_total, var_name = m.groups()
        page = parser.compile_filter(page_name)
    else:
        msg = '%r tag had invalid arguments' % tag_name
        raise template.TemplateSyntaxError(msg)

    return PagerNode(nodelist, page, int(buttons_total), var_name)
