from enum import Enum
from tempfile import NamedTemporaryFile

from flask import send_file


def send_file_from_string(content, mime_type):
    temp_output_file = NamedTemporaryFile()
    with open(temp_output_file.name, 'wb') as writer:
        writer.write(content)
    return send_file(temp_output_file.name, mimetype=mime_type)


class LibreOfficeMimeTypes(Enum):
    odt = 'application/vnd.oasis.opendocument.text'
    ott = 'application/vnd.oasis.opendocument.text-template'
    oth = 'application/vnd.oasis.opendocument.text-web'
    odm = 'application/vnd.oasis.opendocument.text-master'
    otm = 'application/vnd.oasis.opendocument.text-master-template'
    odg = 'application/vnd.oasis.opendocument.graphics'
    otg = 'application/vnd.oasis.opendocument.graphics-template'
    odp = 'application/vnd.oasis.opendocument.presentation'
    otp = 'application/vnd.oasis.opendocument.presentation-template'
    ods = 'application/vnd.oasis.opendocument.spreadsheet'
    ots = 'application/vnd.oasis.opendocument.spreadsheet-template'
    odc = 'application/vnd.oasis.opendocument.chart'
    odf = 'application/vnd.oasis.opendocument.formula'
    odi = 'application/vnd.oasis.opendocument.image'

    docx = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    doc = 'application/msword'

    @staticmethod
    def is_member(mime_type):
        for member in LibreOfficeMimeTypes:
            if member.value == mime_type:
                return True
        return False
