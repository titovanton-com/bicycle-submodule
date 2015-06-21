# -*- coding: utf-8 -*-

import re
import subprocess

from django.db.models import CharField
from sorl.thumbnail.fields import ImageField as SorlImageField
from bicycle.core import forms


class PhoneField(CharField):

    def __init__(self, max_length=None, *args, **kwargs):
        super(PhoneField, self).__init__(max_length=11, *args, **kwargs)

    def formfield(self, form_class=None, **kwargs):
        return super(PhoneField, self).formfield(form_class=forms.PhoneField, **kwargs)

    def to_python(self, value):

        if value is not None:
            value = re.sub('[^0-9]', '', value)

        return super(PhoneField, self).to_python(value)


class PassportField(CharField):

    def __init__(self, max_length=None, *args, **kwargs):
        super(PassportField, self).__init__(max_length=10, *args, **kwargs)

    def to_python(self, value):

        if value is not None:
            value = re.sub('[^0-9]', '', value)

        return super(PassportField, self).to_python(value)


class ExifLessImageField(SorlImageField):

    """Delete all image EXIF meta data right before save"""

    def pre_save(self, model_instance, add):
        f = super(ExifLessImageField, self).pre_save(model_instance, add)

        if f.name:

            try:
                subprocess.check_call(['exiftool', '-all=', '-overwrite_original', f.path])
            except OSError:
                raise Exception('exiftool required for using ExifLessImageField')
            except subprocess.CalledProcessError:
                print 'exiftool returned none-zero exit for %s' % model_instance

        return f
