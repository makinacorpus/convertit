import os
import subprocess


def exists():
    result = subprocess.call(['which', 'unoconv'])
    return result == 0


def register(converters):
    if exists():
        converters['application/vnd.oasis.opendocument.text'] = to_pdf


def to_pdf(source, target):
    """
    Some old version of unoconv do not accept the full target path.
    """
    target_dirname = os.path.dirname(target)

    command = ['unoconv', '-o', target_dirname, '--format', 'pdf', source]
    subprocess.call(command)

    source_basename = os.path.basename(source)
    source_filename, ext = os.path.splitext(source_basename)
    converted_path = os.path.join(target_dirname, source_filename + '.pdf') 
    os.rename(converted_path, target)
