import os
import shutil
import unittest
import filecmp

from .. import svg_to_pdf


here = os.path.dirname(os.path.realpath(__file__))


def inkscape_exists():
    return True


def inkscape_not_exists():
    return False


class OdtToPdfRegisterTests(unittest.TestCase):
    def test_registered_when_inkscape_exists(self):
        converters = {}
        svg_to_pdf.register(converters, inkscape_exists)
        self.assertIn('image/svg+xml', converters)

    def test_not_registered_when_inkscape_not_exists(self):
        converters = {}
        svg_to_pdf.register(converters, inkscape_not_exists)
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
        converted_filepath = svg_to_pdf.svg_to_pdf(self.document_filepath,
            self.temp_dir)
        cmp_result = filecmp.cmp(converted_filepath, self.reference_filepath)

        self.assertTrue(cmp_result)
