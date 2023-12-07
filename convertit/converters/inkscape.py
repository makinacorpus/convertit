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
    dpkg_process = subprocess.Popen(['dpkg', '-s', 'inkscape'], stdout=subprocess.PIPE, text=True)
    grep_process = subprocess.Popen(["grep", "Version"], stdin=dpkg_process.stdout, stdout=subprocess.PIPE, text=True)
    output, error = grep_process.communicate()
    version_str = output.strip().replace("Version: ", "").split('-')[0]
    return version.parse(version_str)


def svg_to_pdf(source, target):
    path = f"{target}/{Path(source).stem}.pdf"

    if get_inkscape_version() < version.parse('1.0'):
        command = [
            'inkscape', '-f', source, '-A', path
        ]
    else:
        command = [
            'inkscape', '--export-filename', path,
        ]
    subprocess.call(command)


def svg_to_png(source, target):
    path = f"{target}/{Path(source).stem}.png"

    if get_inkscape_version() < version.parse('1.0'):
        command = [
            'inkscape', '-f', source, '-e', path]

    else:
        command = [
            'inkscape', '--export-filename', path, ]
    subprocess.call(command)


def converters():
    return {
        (types_map['.svg'], types_map['.pdf']): svg_to_pdf,
        (types_map['.svg'], types_map['.png']): svg_to_png,
    }
