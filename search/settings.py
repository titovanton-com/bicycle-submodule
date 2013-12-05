# -*- coding: utf-8 -*-

from default import rel_project

#   XAPIAN  #
# u have to add 'haystack' to ur INSTALLED_APPS first
try:
    from xapian import QueryParser as XapianQueryParser
    XAPIAN_FLAGS = (
        XapianQueryParser.FLAG_PHRASE |
        XapianQueryParser.FLAG_BOOLEAN |
        XapianQueryParser.FLAG_LOVEHATE |
        XapianQueryParser.FLAG_WILDCARD |
        XapianQueryParser.FLAG_PURE_NOT |
        XapianQueryParser.FLAG_PARTIAL
    )
except ImportError:
    XAPIAN_FLAGS = None
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'xapian_backend.XapianEngine', 
        'PATH': rel_project('search', 'xapian_index'),
        'INCLUDE_SPELLING': True,
        'FLAGS': XAPIAN_FLAGS,
    },
}
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 12
HAYSTACK_XAPIAN_LANGUAGE = 'ru'
HAYSTACK_DEFAULT_OPERATOR = 'OR'