# -*- coding: utf-8 -*-

import os


PROJECT_URL = 'sub.localsite.com'
tmp = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.split(tmp)[0]
PROJECT_ROOT = os.path.split(APP_ROOT)[0]


def rel_project(*x):
    return os.path.join(PROJECT_ROOT, *x)


def rel_mainapp(*x):
    return os.path.join(APP_ROOT, *x)


def rel_url(*x):
    return 'http://%s/' % os.path.join(PROJECT_URL, *x)
