from mimetypes import types_map
from pathlib import Path

import cairosvg

pdf_mimetype = 'application/pdf'
svg_mimetype = 'image/svg+xml'


def is_available():
    return True


def svg_to_pdf(source, target):
    path = f"{target}/{Path(source).stem}.pdf"
    cairosvg.svg2pdf(url=source, write_to=path)


def svg_to_png(source, target):
    path = f"{target}/{Path(source).stem}.png"
    cairosvg.svg2png(url=source, write_to=path)


def converters():
    return {
        (types_map['.svg'], types_map['.pdf']): svg_to_pdf,
        (types_map['.svg'], types_map['.png']): svg_to_png,
    }
