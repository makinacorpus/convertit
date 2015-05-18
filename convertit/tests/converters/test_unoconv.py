import os
import shutil
from mock import patch, sentinel

from convertit.converters import unoconv
from convertit.tests.unittest import unittest


here = os.path.dirname(os.path.realpath(__file__))


class UnoconvConvertionTests(unittest.TestCase):
    temp_dir = os.path.join(here, '../data/tmp')
    odt_filepath = os.path.join(here, '../data/test_document.odt')
    pdf_filepath = os.path.join(here, '../data/test_document.pdf')

    def setUp(self):
        if not unoconv.is_available():
            self.skipTest('unoconv not found')

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        os.makedirs(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_odt_to_pdf_conversion(self):
        converted_filepath = os.path.join(self.temp_dir, 'test_document.pdf')
        unoconv.to_pdf(self.odt_filepath, converted_filepath)
        self.assertTrue(os.path.exists(converted_filepath))


class UnoconvCommandTests(unittest.TestCase):

    @patch('convertit.converters.unoconv.Lock')
    @patch('convertit.converters.unoconv.os')
    @patch('convertit.converters.unoconv.subprocess')
    def test_adds_quality_option_when_given(self, subprocess_mock, os_mock, LockMock):
        unoconv.unoconv(sentinel.output_path,
                        sentinel.output_format,
                        sentinel.source,
                        quality=100)

        subprocess_mock.Popen.assert_called_with([
                'unoconv',
                '-o', sentinel.output_path,
                '--format', sentinel.output_format,
                '-e', 'Quality=100',
                sentinel.source
            ],
            env=os_mock.environ.copy(),
            stdout=subprocess_mock.PIPE,
            stderr=subprocess_mock.PIPE
        )


class UnoconvCoverterTests(unittest.TestCase):

    def test_options_declaration(self):
        converter = unoconv.Converter(sentinel.output_format, sentinel.options)

        self.assertEqual(converter.options, sentinel.options)

    @patch('convertit.converters.unoconv.convert')
    def test_convert_call_pass_arguments(self, convert_mock):
        converter = unoconv.Converter(sentinel.output_format, sentinel.options)

        converter(
            sentinel.source,
            sentinel.target,
            quality=sentinel.quality)

        convert_mock.assert_called_with(
            sentinel.source,
            sentinel.target,
            sentinel.output_format,
            quality=sentinel.quality)


class ToPdfTests(unittest.TestCase):

    def test_it_has_a_quality_option_declared(self):
        self.assertEqual(unoconv.to_pdf.options, {
            'quality': {
                'type': int
            }
        })
