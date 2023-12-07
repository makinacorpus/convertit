import subprocess
from mimetypes import types_map
from pathlib import Path

from packaging import version

from convertit import exists

pdf_mimetype = 'application/pdf'
svg_mimetype = 'image/svg+xml'


def is_available():
    return exists('inkscape')


def get_inkscape_version():
    version_str = subprocess.check_output([
        'dpkg', '-s', 'inkscape',
        '|', 'grep' 'Version'
    ]).strip()
    return version.parse(version_str.replace("Version: ", ""))


def svg_to_pdf(source, target):
    if get_inkscape_version() < version.parse('1.0'):
        command = [
            'inkscape', '-f', source, '-A', target
        ]
    else:
        path = f"{target}/{Path(source).stem}.pdf"
        command = [
            'inkscape', '--export-filename', path,
        ]
    subprocess.call(command)


def svg_to_png(source, target):
    if get_inkscape_version() < version.parse('1.0'):
        command = [
            'inkscape', '-f', source, '-e', target]

    else:
        path = f"{target}/{Path(source).stem}.png"
        command = [
            'inkscape', '--export-filename', path, ]
    subprocess.call(command)


def converters():
    return {
        (types_map['.svg'], types_map['.pdf']): svg_to_pdf,
        (types_map['.svg'], types_map['.png']): svg_to_png,
    }
