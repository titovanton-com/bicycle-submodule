# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.finders import BaseStorageFinder


class StaticSrcStorageFinder(BaseStorageFinder):
    storage = FileSystemStorage(settings.STATIC_SRC)
