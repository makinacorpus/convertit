import subprocess
import  convertit as c

def to_pdf(source, target):
    command = [
        'inkscape', '-f', source, '-A', target]
    subprocess.call(command)



def register(converters=None):
    c.register(('image/svg+xml','application/pdf'), 'pdf', to_pdf, c.test_program('inkscape'),
               converters=converters)

register()


