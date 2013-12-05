# -*- coding: utf-8 -*-

import re

from haystack.query import SearchQuerySet
from haystack.query import EmptySearchQuerySet


quotes_re = re.compile(r'([\'"].*?[\'"])', re.S)


def make_search_queryset(query_string, queryset_class=SearchQuerySet, empty_queryset_class=EmptySearchQuerySet):
    '''
    .. sectionauthor:: Василий Шередеко (piphon@gmail.com)
    '''
    query_string = query_string.strip()
    if query_string:
        # Разбиваем на группы для поиска
        query_parts = []
        query_quotes = quotes_re.split(query_string)
        query_quotes = filter(None, [qp.strip() for qp in query_quotes])
        for qp in query_quotes:
            if qp[0] == '"' or qp[0] == "\"":
                query_parts.append(qp[1:-1])
            else:
                query_spaces = filter(None, [qp.strip() for qp in qp.split(' ')])
                for qs in query_spaces:
                    query_parts.append(qs)

    # Включаем эти группы в поиск
    queryset = queryset_class()
    for qp in query_parts:
        queryset_part = queryset_class().filter_or(content__startswith=qp).filter_or(content=qp)

        suggestion = SearchQuerySet().filter(content__startswith=qp).spelling_suggestion()
        if suggestion:
            queryset_part = queryset_part.filter_or(
                content__startswith=suggestion).filter_or(content=suggestion)
        queryset &= queryset_part
        return queryset
    else:
        queryset = empty_queryset_class()
    return queryset
