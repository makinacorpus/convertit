import os
import subprocess
import convertit as c


def uno_transform(output_fmt='pdf', output_ext=None):
    if not output_ext:
        output_ext = output_fmt

    def to_format(source, target):
        """
        Some old version of unoconv do not accept the full target path.
        """
        target_dirname = os.path.dirname(target)
        command = ['unoconv', '-o', target_dirname, '--format', output_fmt, source]
        env = os.environ.copy()
        # do not mess pyuno pythonpath !
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']
        p = subprocess.Popen(command, stdout=subprocess.PIPE, env=env, stderr=subprocess.PIPE)
        p.wait()
        output = '\n'.join([p.stdout.read(), p.stderr.read()])
        source_basename = os.path.basename(source)
        source_filename, ext = os.path.splitext(
            source_basename)
        converted_path = os.path.join(
            target_dirname,
            source_filename + '.' + output_ext)
        if not os.path.exists(converted_path):
            raise c.TransformError(output)
        os.rename(converted_path, target)
    return to_format

to_pdf = uno_transform('pdf')
to_doc = uno_transform('doc')


def register(converters=None):
    c.register(('application/vnd.oasis.opendocument.text', 'application/pdf'),
               'pdf', to_pdf, c.test_program('unoconv'),
               converters=converters)
    c.register(('application/vnd.oasis.opendocument.text', 'application/msword'),
               'doc', to_doc, c.test_program('unoconv'),
               converters=converters)

register()
