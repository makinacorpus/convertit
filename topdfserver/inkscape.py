import subprocess


def inkscape_exists():
    result = subprocess.call(['which', 'inkscape'])
    if result == 0:
        return True
    else:
        return False


def register(converters):
    if inkscape_exists():
        converters['image/svg+xml'] = to_pdf


def to_pdf(source, target):
    command = ['inkscape', '-f', source, '-A', target]
    subprocess.call(command)
