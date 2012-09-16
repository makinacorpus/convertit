import os
import shutil
import subprocess


def unoconv_exists():
    result = subprocess.call(['which', 'unoconv'])
    if result == 0:
        return True
    else:
        return False


def register(converters):
    if unoconv_exists():
        converters['application/vnd.oasis.opendocument.text'] = odt_to_pdf


def odt_to_pdf(source, target):
    """
    Some old version of unoconv do not accept the full target path.
    """
    command = ['unoconv', '--format', 'pdf', source]
    subprocess.call(command)
    shutil.move(os.path.splitext(source)[0] + '.pdf', target)
