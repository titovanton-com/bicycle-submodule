# -*- coding: utf-8 -*-

import os


tmp = os.path.abspath(os.path.dirname(__file__))
BICYCLE_ROOT = tmp


def rel_bicycle(*x):
    return os.path.join(BICYCLE_ROOT, *x)
