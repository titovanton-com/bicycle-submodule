# coding: utf-8

from sorl.thumbnail.fields import ImageField

from bicycle.qrcode.utilites import upload_qr_code


class QRCodeField(ImageField):

    def __init__(self, **kwargs):
        tmp = {
            'editable': False,
            'verbose_name': u'QR Код',
            'upload_to': upload_qr_code,
        }
        kwargs.update(tmp)
        super(QRCodeField, self).__init__(**kwargs)
