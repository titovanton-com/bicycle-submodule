# coding: utf-8

import os

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from sorl.thumbnail import get_thumbnail
import qrcode

from bicycle.qrcode.factories.image_magick import MagickImage
from fields import QRCodeField


class QRCodeMixin(models.Model):
    qr_code = QRCodeField()

    def qr_code_admin(self):
        if self.qr_code.name:
            image_path = os.path.join(settings.MEDIA_ROOT, str(self.qr_code))
        else:
            image_path = os.path.join(settings.MEDIA_ROOT, 'noimage.png')
        try:
            thumbnail = get_thumbnail(image_path, '100', format='PNG')
        except IOError:
            return u'QR кода нет'
        else:
            return u'<a href="%s/"><img src="%s"/></a>' % (self.pk, thumbnail.url)
    qr_code_admin.short_description = u'QR Код'
    qr_code_admin.allow_tags = True

    def qr_background(self, img):
        return (
            # bg_img, left, top
        )

    def qr_settings(self):
        """ QRCode settings

        https://github.com/lincolnloop/python-qrcode
        """
        return {}

    def qr_encode_data(self):
        return self.get_url()

    def save(self, *args, **kwargs):
        stngs = {
            'border': 0,
            'fit': True,
        }
        stngs.update(self.qr_settings())
        qr = qrcode.QRCode(border=stngs['border'])
        qr.add_data(self.qr_encode_data())
        qr.make(fit=stngs['fit'])
        img = qr.make_image(image_factory=MagickImage)
        background = self.qr_background(img)
        name = 'qr.png'
        if background:
            bg_img, left, top = background
            bg_img.composite(img._img, left, top)
            blob = bg_img.make_blob()
        else:
            blob = img.get_blob()
        self.qr_code.save(name, ContentFile(blob), save=False)
        super(QRCodeMixin, self).save(*args, **kwargs)

    class Meta(object):
        abstract = True
