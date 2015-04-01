import os
import shutil

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
