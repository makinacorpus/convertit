import os
import subprocess


def register(converters):
    inkscape = subprocess.check_output(['which', 'inkscape'])

    if inkscape:
        converters['image/svg+xml'] = svg_to_pdf


def svg_to_pdf(filepath, target_dir):
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    target_file =  '/'.join([target_dir, filename]) + '.pdf'
    command = ['inkscape', '-f', filepath, '-A', target_file]
    subprocess.call(command)
    return os.path.join(target_dir, filename + '.pdf')
