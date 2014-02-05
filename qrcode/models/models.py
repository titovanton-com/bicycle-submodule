# coding: utf-8

import os

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from sorl.thumbnail import get_thumbnail
from bicycle.qrcode.factories.image_magick import MagickImage
import qrcode

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

    def qr_background(self, qrc):
        return (
            # bg_img, left, top
        )

    def qr_make_qrcode(self, stngs):
        qr = qrcode.QRCode(border=stngs['border'])
        qr.add_data(self.qr_encode_data())
        qr.make(fit=stngs['fit'])
        factory_img = qr.make_image(image_factory=MagickImage)
        return factory_img._img

    def qr_settings(self):
        """ QRCode settings

        https://github.com/lincolnloop/python-qrcode
        """
        return {}

    def qr_encode_data(self):
        return self.get_url()

    def qr_qrcode(self, *args, **kwargs):
        if self.qr_encode_data():
            stngs = {
                'border': 0,
                'fit': True,
            }
            stngs.update(self.qr_settings())
            qrc = self.qr_make_qrcode(stngs)
            background = self.qr_background(qrc)
            name = 'qr.png'
            if background:
                bg_img, left, top = background
                bg_img.composite(qrc, left, top)
                bg_img.format = 'PNG'
                blob = bg_img.make_blob()
            else:
                qrc.format = 'PNG'
                blob = qrc.make_blob()
            self.qr_code.save(name, ContentFile(blob), save=False)

    def save(self, *args, **kwargs):
        self.qr_qrcode(*args, **kwargs)
        super(QRCodeMixin, self).save(*args, **kwargs)

    class Meta(object):
        abstract = True
