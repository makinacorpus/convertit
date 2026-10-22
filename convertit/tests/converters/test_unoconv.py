import os
import shutil
import unittest
from unittest.mock import MagicMock, patch

from django.test import TestCase

from convertit.converters import unoconv

here = os.path.dirname(os.path.realpath(__file__))


class UnoconvConvertionTests(TestCase):
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
        unoconv.to_pdf(self.odt_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(converted_filepath))

    def test_setup_existing_temp_dir_and_unavailable(self):
        self.setUp()
        self.assertTrue(os.path.exists(self.temp_dir))
        with patch.object(unoconv, 'is_available', return_value=False):
            with self.assertRaises(unittest.SkipTest):
                self.setUp()

    @patch('subprocess.Popen')
    def test_unoconv_removes_pythonpath(self, mock_popen):
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc
        with patch.dict(os.environ, {'PYTHONPATH': '/some/path'}):
            unoconv.unoconv(self.temp_dir, 'pdf', self.odt_filepath)
        called_env = mock_popen.call_args.kwargs['env']
        self.assertNotIn('PYTHONPATH', called_env)

    @patch.object(unoconv, 'unoconv')
    def test_convert_raises_ioerror_when_target_missing(self, mock_unoconv):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout.read.return_value = b'out'
        mock_proc.stderr.read.return_value = b'err'
        mock_unoconv.return_value = mock_proc
        with self.assertRaises(IOError):
            unoconv.convert(self.odt_filepath, self.temp_dir, 'pdf')
