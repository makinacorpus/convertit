import os
import subprocess
import convertit as c

ext = 'pdf'
def to_pdf(source, target):
    """
    Some old version of unoconv do not accept the full target path.
    """
    target_dirname = os.path.dirname(target)
    command = ['unoconv', '-o', target_dirname, '--format', 'pdf', source]
    env = os.environ.copy()
    # do not mess pyuno pythonpath !
    if 'PYTHONPATH' in env:
        del env['PYTHONPATH']
    p = subprocess.Popen(command, stdout=subprocess.PIPE, env = env, stderr=subprocess.PIPE)
    p.wait()
    output = '\n'.join([p.stdout.read(), p.stderr.read()])
    source_basename = os.path.basename(source)
    source_filename, ext = os.path.splitext(
        source_basename)
    converted_path = os.path.join(
        target_dirname,
        source_filename + '.pdf')
    if not os.path.exists(converted_path):
        raise c.TransformError(output)
    os.rename(converted_path, target)


def register(converters=None):
    c.register(('application/vnd.oasis.opendocument.text', 'application/pdf'),
               ext, to_pdf, c.test_program('unoconv'),
               converters=converters)
register()


