import fcntl
import logging
import os
import subprocess
import tempfile
from functools import partial

from convertit import exists

log = logging.getLogger(__name__)


class Lock:
    def __init__(self, filename):
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(filename, 'wb')

    def acquire(self):
        fcntl.flock(self.handle, fcntl.LOCK_EX)

    def release(self):
        fcntl.flock(self.handle, fcntl.LOCK_UN)

    def __del__(self):
        self.handle.close()


def unoconv(output_path, output_format, source):
    command = [
        'libreoffice', '--headless',
        '--convert-to', output_format,
        '--outdir', output_path, source
    ]

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
    log.error('Converting %s to %s with %s', source, target, output_format)
    p = unoconv(target, output_format, source)
    output = b'\n'.join([p.stdout.read(), p.stderr.read()])
    log.error(output)
    filename = os.path.basename(source)
    # replace extenson with output_frmat
    filename, _ = os.path.splitext(filename)
    filename = filename + '.' + output_format

    target_file = os.path.join(target, filename)

    if not os.path.exists(target_file):
        raise IOError(p.returncode, output.decode())


to_doc = partial(convert, output_format='doc')
to_docx = partial(convert, output_format='docx')
to_ods = partial(convert, output_format='ods')
to_odt = partial(convert, output_format='odt')
to_pdf = partial(convert, output_format='pdf')
to_xls = partial(convert, output_format='xls')
to_xlsx = partial(convert, output_format='xlsx')

PLAIN_TEXT = 'plain/text'
ODT_MIMETYPE = 'application/vnd.oasis.opendocument.text'
ODS_MIMETYPE = 'application/vnd.oasis.opendocument.spreadsheet'
DOC_MIMETYPE = 'application/msword'
DOCX_MIMETYPE = (
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
)
XLS_MIMETYPE = 'application/vnd.ms-excel'
XLSX_MIMETYPE = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
PDF_MIMETYPE = 'application/pdf'


def is_available():
    return exists('libreoffice')


def converters():
    return {
        (PLAIN_TEXT, ODS_MIMETYPE): to_ods,
        (PLAIN_TEXT, XLS_MIMETYPE): to_xls,
        (PLAIN_TEXT, XLSX_MIMETYPE): to_xlsx,
        (ODS_MIMETYPE, XLS_MIMETYPE): to_xls,
        (ODS_MIMETYPE, XLSX_MIMETYPE): to_xlsx,
        (XLS_MIMETYPE, XLSX_MIMETYPE): to_xlsx,
        (XLSX_MIMETYPE, PDF_MIMETYPE): to_pdf,
        (XLSX_MIMETYPE, ODS_MIMETYPE): to_ods,
        (XLSX_MIMETYPE, XLS_MIMETYPE): to_xls,
        (ODT_MIMETYPE, DOC_MIMETYPE): to_doc,
        (ODT_MIMETYPE, DOCX_MIMETYPE): to_docx,
        (ODT_MIMETYPE, PDF_MIMETYPE): to_pdf,
        (DOC_MIMETYPE, DOCX_MIMETYPE): to_docx,
        (DOCX_MIMETYPE, PDF_MIMETYPE): to_pdf,
        (DOCX_MIMETYPE, ODT_MIMETYPE): to_odt,
        (DOCX_MIMETYPE, DOC_MIMETYPE): to_doc,
    }
