# coding: UTF-8

import redis
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        c = settings.REDIS_CONNECTION
        r = redis.Redis(**c)
        for const in settings.CONSTANCE_CONFIG:
            r.delete(settings.CONSTANCE_REDIS_PREFIX + const)
