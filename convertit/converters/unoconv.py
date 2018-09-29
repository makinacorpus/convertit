import fcntl
import os
import subprocess
import tempfile
from functools import partial
from mimetypes import types_map

from convertit import exists


class Lock:
    def __init__(self, filename):
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(filename, 'w')

    def acquire(self):
        fcntl.flock(self.handle, fcntl.LOCK_EX)

    def release(self):
        fcntl.flock(self.handle, fcntl.LOCK_UN)

    def __del__(self):
        self.handle.close()


def unoconv(output_path, output_format, source):
    # WARNING: Some old version of unoconv do not accept the full target path.
    #          So output_path must be a directory.
    command = ['unoconv', '-o', output_path, '--format', output_format, source]

    # Do not mess pyuno pythonpath !
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        del env['PYTHONPATH']

    try:
        lock = Lock(os.path.join(tempfile.gettempdir(), "convertit.lock"))
        lock.acquire()
        p = subprocess.Popen(command, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
    finally:
        lock.release()

    return p


def convert(source, target, output_format):
    p = unoconv(target, output_format, source)
    output = '\n'.join([p.stdout.read(), p.stderr.read()])
    if not os.path.exists(target):
        raise IOError(p.returncode, output)


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
        (types_map['.doc'], types_map['.pdf']): to_pdf,
        (types_map['.docx'], types_map['.pdf']): to_pdf,
        (types_map['.ppt'], types_map['.pdf']): to_pdf,
        (types_map['.pptx'], types_map['.pdf']): to_pdf
    }
