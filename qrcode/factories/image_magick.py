# coding: utf-8

from qrcode.image.base import BaseImage
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color


class MagickImage(BaseImage):

    """
    ImageMagick based factory
    """
    kind = 'PNG'
    allowed_kinds = ('PNG', 'JPG')

    def new_image(self, **kwargs):
        return Image(width=self.pixel_size, height=self.pixel_size)

    def drawrect(self, row, col):
        draw = Drawing()
        draw.fill_color = Color('black')
        (x, y), (x2, y2) = self.pixel_box(row, col)
        for r in range(self.box_size):
            line_y = y + r
            draw.line((x, line_y), (x2, line_y))
            draw(self._img)

    def save(self, stream, kind=None):
        self._img.format = kind is None and self.kind or self.check_kind(kind)
        self._img.save(file=stream)

    def get_blob(self, kind=None):
        self._img.format = kind is None and self.kind or self.check_kind(kind)
        return self._img.make_blob()

    def check_kind(self, kind, transform=None, **kwargs):
        """
        pymaging (pymaging_png at least) uses lower case for the type.
        """

        if transform is None:
            transform = lambda x: x.lower()
        return super(MagickImage, self).check_kind(
            kind, transform=transform, **kwargs)

    def get_width(self):
        return self._img.width

    def get_height(self):
        return self._img.height