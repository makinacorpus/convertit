import os
import shutil

from django.test import TestCase

from convertit.converters import cairosvg

here = os.path.dirname(os.path.realpath(__file__))


class CairosvgConvertionTests(TestCase):
    temp_dir = os.path.join(here, '../data/tmp')
    svg_filepath = os.path.join(here, '../data/test_svg.svg')
    pdf_filepath = os.path.join(here, '../data/test_svg.pdf')

    def setUp(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        os.makedirs(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_svg_to_pdf_conversion(self):
        converted_filepath = os.path.join(self.temp_dir, 'test_svg.pdf')
        cairosvg.svg_to_pdf(self.svg_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(converted_filepath))

    def test_svg_to_png_conversion(self):
        converted_filepath = os.path.join(self.temp_dir, 'test_svg.png')
        cairosvg.svg_to_png(self.svg_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(converted_filepath))

    def test_is_available_and_existing_temp_dir(self):
        self.assertTrue(cairosvg.is_available())
        self.setUp()
        self.assertTrue(os.path.exists(self.temp_dir))
