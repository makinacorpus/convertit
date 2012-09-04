import os
import shutil
import unittest
import filecmp

from mock import patch

from .. import svg_to_pdf


here = os.path.dirname(os.path.realpath(__file__))


class OdtToPdfRegisterTests(unittest.TestCase):
    @patch('topdfserver.svg_to_pdf.inkscape_exists')
    def test_registered_when_inkscape_exists(self, inkscape_exists):
        inkscape_exists.return_value = True
        converters = {}
        svg_to_pdf.register(converters)
        self.assertIn('image/svg+xml', converters)

    @patch('topdfserver.svg_to_pdf.inkscape_exists')
    def test_not_registered_when_inkscape_not_exists(self, inkscape_exists):
        inkscape_exists.return_value = False
        converters = {}
        svg_to_pdf.register(converters)
        self.assertNotIn('image/svg+xml', converters)


class OdtToPdfConvertionTests(unittest.TestCase):
    temp_dir = os.path.join(here, 'data/tmp')
    document_filepath = os.path.join(here, 'data/test_svg.svg')
    reference_filepath = os.path.join(here, 'data/test_svg.pdf')

    def setUp(self):
        if not svg_to_pdf.inkscape_exists():
            self.skipTest('inkscape not found')

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        os.makedirs(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_svg_conversion(self):
        converted_filepath = os.path.join(self.temp_dir, 'test_svg.pdf')
        svg_to_pdf.svg_to_pdf(self.document_filepath, converted_filepath)
        cmp_result = filecmp.cmp(converted_filepath, self.reference_filepath)

        self.assertTrue(cmp_result)
