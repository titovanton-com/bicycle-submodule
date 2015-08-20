# -*- coding: utf-8 -*-

import re


def get_xml_ns(content):
    mutches = re.findall(r'xmlns\:?([^=]*?)=("(.+?)"|\'(.+?)\')', content, re.MULTILINE)
    ns = {i[0]: i[2] or i[3] for i in mutches}
    ns['default'] = ns['']
    return ns
