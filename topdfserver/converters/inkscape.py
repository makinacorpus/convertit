import subprocess


def exists():
    result = subprocess.call(['which', 'inkscape'])
    return result == 0


def register(converters):
    if exists():
        converters['image/svg+xml'] = to_pdf


def to_pdf(source, target):
    command = ['inkscape', '-f', source, '-A', target]
    subprocess.call(command)
