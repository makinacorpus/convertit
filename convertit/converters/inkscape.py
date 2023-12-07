import os
import subprocess
from mimetypes import types_map
from pathlib import Path
from convertit import exists

INKSCAPE_MAIN_VERSION = 1
pdf_mimetype = 'application/pdf'
svg_mimetype = 'image/svg+xml'


def is_available():
    return exists('inkscape')

def check_inkscape_version():
    return subprocess.check_output(['inkscape', '--version']).strip()

def svg_to_pdf(source, target):
    raise Exception(check_inkscape_version())
    path = f"{target}/{Path(source).stem}.pdf"

    if INKSCAPE_MAIN_VERSION:
        command = [
            'inkscape', '--export-filename', path,
        ]
    else:
        command = [
            'inkscape', '-f', source, '-A', target
        ]
    subprocess.call(command)


def svg_to_png(source, target):
    path = f"{target}/{Path(source).stem}.png"
    if INKSCAPE_MAIN_VERSION:
        command = [
            'inkscape', '--export-filename', path, ]
    else:
        command = [
            'inkscape', '-f', source, '-e', target]
    subprocess.call(command)


def converters():
    return {
        (types_map['.svg'], types_map['.pdf']): svg_to_pdf,
        (types_map['.svg'], types_map['.png']): svg_to_png,
    }
