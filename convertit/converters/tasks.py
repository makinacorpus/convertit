import os
import subprocess
from celery import Celery
from pyramid.threadlocal import get_current_registry

from convertit import exists


app = Celery('tasks', backend='amqp', broker='amqp://localhost//')
app.conf.update(CELERY_ACCEPT_CONTENT=['pickle'])


def unoconv(output_path, output_format, source):
    # WARNING: Some old version of unoconv do not accept the full target path.
    #          So output_path must be a directory.
    command = ['unoconv', '-o', output_path, '--format', output_format, source]

    # Do not mess pyuno pythonpath !
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        del env['PYTHONPATH']

    p = subprocess.Popen(command, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    return p


@app.task
def convert(source, target, output_format):
    output_path = os.path.dirname(target)
    source_filename = os.path.splitext(os.path.basename(source))[0]
    converted_basename = source_filename + '.' + output_format
    converted_path = os.path.join(output_path, converted_basename)

    p = unoconv(output_path, output_format, source)
    output = '\n'.join([p.stdout.read(), p.stderr.read()])

    if not os.path.exists(converted_path):
        raise IOError(p.returncode, output)

    os.rename(converted_path, target)
