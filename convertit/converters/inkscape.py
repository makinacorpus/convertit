import subprocess
from mimetypes import types_map
from pathlib import Path
from convertit import exists


pdf_mimetype = 'application/pdf'
svg_mimetype = 'image/svg+xml'


def is_available():
    return exists('inkscape')


def svg_to_pdf(source, target):
    path = f"{target}/{Path(source).stem}.pdf"

    command = [
        'inkscape', '--export-filename', path, ]
    subprocess.call(command)


def svg_to_png(source, target):
    path = f"{target}/{Path(source).stem}.png"

    command = [
        'inkscape', '--export-filename', path, ]
    subprocess.call(command)


def converters():
    return {
        (types_map['.svg'], types_map['.pdf']): svg_to_pdf,
        (types_map['.svg'], types_map['.png']): svg_to_png,
    }
