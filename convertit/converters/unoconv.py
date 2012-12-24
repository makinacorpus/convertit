import os
import subprocess
from functools import partial
from mimetypes import types_map

from convertit import exists


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


def convert(source, target, output_format):
    output_path = os.path.dirname(target)
    source_filename = os.path.splitext(os.path.basename(source))[0]
    converted_basename = source_filename + '.' + output_format
    converted_path = os.path.join(output_path, converted_basename)

    p = unoconv(output_path, output_format, source)
    output = '\n'.join([p.stdout.read(), p.stderr.read()])

    if not os.path.exists(converted_path):
        raise IOError(p.return_code, output)

    os.rename(converted_path, target)


to_doc = partial(convert, output_format='doc')
to_ods = partial(convert, output_format='ods')
to_pdf = partial(convert, output_format='pdf')
to_xls = partial(convert, output_format='xls')


def is_available():
    return exists('unoconv')


def converters():

    return {
        (types_map['.csv'], types_map['.ods']): to_ods,
        (types_map['.csv'], types_map['.xls']): to_xls,
        (types_map['.ods'], types_map['.xls']): to_xls,
        (types_map['.odt'], types_map['.doc']): to_doc,
        (types_map['.odt'], types_map['.pdf']): to_pdf,
    }
