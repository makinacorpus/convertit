import os
import shutil

from convertit.converters import inkscape
from convertit.tests.unittest import unittest


here = os.path.dirname(os.path.realpath(__file__))


class InkscapeConvertionTests(unittest.TestCase):
    temp_dir = os.path.join(here, '../data/tmp')
    svg_filepath = os.path.join(here, '../data/test_svg.svg')
    pdf_filepath = os.path.join(here, '../data/test_svg.pdf')

    def setUp(self):
        if not inkscape.is_available():
            self.skipTest('inkscape not found')

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        os.makedirs(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_svg_to_pdf_conversion(self):
        converted_filepath = os.path.join(self.temp_dir, 'test_svg.pdf')
        inkscape.svg_to_pdf(self.svg_filepath, converted_filepath)
        self.assertTrue(os.path.exists(converted_filepath))

    def test_svg_to_png_conversion(self):
        converted_filepath = os.path.join(self.temp_dir, 'test_svg.png')
        inkscape.svg_to_png(self.svg_filepath, converted_filepath)
        self.assertTrue(os.path.exists(converted_filepath))
