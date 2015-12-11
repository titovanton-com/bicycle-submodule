# coding: utf-8

import os

from bicycle.core.tools import valid_file_name


def upload_qr_code(instance, filename):
    return os.path.join(u'%s_qr_code' % instance.__class__.__name__.lower(),
                        valid_file_name(filename))
