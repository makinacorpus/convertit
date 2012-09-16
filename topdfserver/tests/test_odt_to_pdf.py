import os
import shutil
import unittest

from mock import patch

from .. import odt_to_pdf


here = os.path.dirname(os.path.realpath(__file__))


class OdtToPdfRegisterTests(unittest.TestCase):
    @patch('topdfserver.odt_to_pdf.unoconv_exists')
    def test_registered_when_unoconv_exists(self, unoconv_exists):
        unoconv_exists.return_value = True
        converters = {}
        odt_to_pdf.register(converters)
        self.assertIn('application/vnd.oasis.opendocument.text', converters)

    @patch('topdfserver.odt_to_pdf.unoconv_exists')
    def test_not_registered_when_unoconv_not_exists(self, unoconv_exists):
        unoconv_exists.return_value = False
        converters = {}
        odt_to_pdf.register(converters)
        self.assertNotIn('application/vnd.oasis.opendocument.text', converters)


class OdtToPdfConvertionTests(unittest.TestCase):
    datadir = os.path.join(here, 'data')
    temp_dir = os.path.join(here, 'data/tmp')
    document_filepath = os.path.join(here, 'data/test_document.odt')
    reference_filepath = os.path.join(here, 'data/test_document.pdf')

    def setUp(self):
        if not odt_to_pdf.unoconv_exists():
            self.skipTest('unoconv not found')

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        os.makedirs(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_odt_conversion(self):
        downlowded_filepath = os.path.join(self.temp_dir, 'test_document.odt')
        converted_filepath = os.path.join(self.temp_dir, 'test_document.pdf')

        shutil.copy(self.document_filepath, self.temp_dir)

        odt_to_pdf.odt_to_pdf(downlowded_filepath, converted_filepath)
        self.assertTrue(os.path.exists(converted_filepath))
