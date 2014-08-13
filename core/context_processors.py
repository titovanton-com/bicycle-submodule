# -*- coding: utf-8 -*-

from django.conf import settings


def cache_timeout(request):
    return {'CACHE_TIMEOUT': getattr(settings, 'CACHE_TIMEOUT', 60 * 5)}
