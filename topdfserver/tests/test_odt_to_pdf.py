import os
import shutil
import unittest
import filecmp

from .. import odt_to_pdf


here = os.path.dirname(os.path.realpath(__file__))


def unoconv_exists():
    return True


def unoconv_not_exists():
    return False


class OdtToPdfRegisterTests(unittest.TestCase):
    def test_registered_when_unoconv_exists(self):
        converters = {}
        odt_to_pdf.register(converters, unoconv_exists)
        self.assertIn('application/vnd.oasis.opendocument.text', converters)

    def test_not_registered_when_unoconv_not_exists(self):
        converters = {}
        odt_to_pdf.register(converters, unoconv_not_exists)
        self.assertNotIn('application/vnd.oasis.opendocument.text', converters)


class OdtToPdfConvertionTests(unittest.TestCase):
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
        converted_filepath = odt_to_pdf.odt_to_pdf(self.document_filepath,
            self.temp_dir)

        reference_basename = os.path.basename(self.reference_filepath)
        converted_basename = os.path.basename(converted_filepath)

        reference_size = os.path.getsize(self.reference_filepath)
        converted_size = os.path.getsize(converted_filepath)

        self.assertEquals(converted_size, reference_size)
        self.assertEquals(converted_basename, reference_basename)
