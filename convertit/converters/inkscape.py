import subprocess
from mimetypes import types_map

from convertit import exists


pdf_mimetype = 'application/pdf'
svg_mimetype = 'image/svg+xml'


def is_available():
    return exists('inkscape')


def svg_to_pdf(source, target):
    command = [
        'inkscape', '-f', source, '-A', target]
    subprocess.call(command)


def converters():
    return {
        (types_map['.svg'], types_map['.pdf']): svg_to_pdf,
    }
