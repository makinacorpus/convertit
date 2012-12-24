import subprocess

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
        (svg_mimetype, pdf_mimetype): svg_to_pdf,
    }
