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
    command = ['unoconv', '-o', target, '--format', 'pdf', source]
    subprocess.call(command)
