from functools import partial
from mimetypes import types_map

from convertit import exists
from convertit.converters import tasks
from pyramid.settings import asbool


def convert(source, target, settings, output_format):
    if asbool(settings['convertit.serialize_unoconv_calls']):
        handler = tasks.convert.delay(source, target, output_format)
        handler.wait(timeout=int(settings['convertit.unoconv_timeout']))
    else:
        tasks.convert(source, target, output_format)


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
