import os
import subprocess


def register(converters):
    unoconv = subprocess.check_output(['which', 'unoconv'])
    print(unoconv)

    if unoconv:
        converters['application/vnd.oasis.opendocument.text'] = odt_to_pdf


def odt_to_pdf(filepath, target_dir):
    command = ['unoconv', '-o', target_dir, '--format', 'pdf',
        filepath]
    subprocess.call(command)
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    return os.path.join(target_dir, filename + '.pdf')
