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
    docx_filepath = os.path.join(here, '../data/test_document.docx')
    xlsx_filepath = os.path.join(here, '../data/test_spreadsheet.xlsx')
    csv_filepath = os.path.join(here, '../data/test_spreadsheet.csv')
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

    def test_odt_to_docx_conversion(self):
        converted_filepath = os.path.join(self.temp_dir, 'test_document.docx')
        unoconv.to_docx(self.odt_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(converted_filepath))

    def test_docx_conversions(self):
        unoconv.to_pdf(self.docx_filepath, self.temp_dir)
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, 'test_document.pdf'))
        )
        unoconv.to_odt(self.docx_filepath, self.temp_dir)
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, 'test_document.odt'))
        )
        unoconv.to_doc(self.docx_filepath, self.temp_dir)
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, 'test_document.doc'))
        )

    def test_xlsx_conversions(self):
        unoconv.to_pdf(self.xlsx_filepath, self.temp_dir)
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, 'test_spreadsheet.pdf'))
        )
        ods_filepath = os.path.join(self.temp_dir, 'test_spreadsheet.ods')
        unoconv.to_ods(self.xlsx_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(ods_filepath))
        xls_filepath = os.path.join(self.temp_dir, 'test_spreadsheet.xls')
        unoconv.to_xls(self.xlsx_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(xls_filepath))

        # Also test converting ods and xls back to xlsx
        ods_to_xlsx_dir = os.path.join(self.temp_dir, 'from_ods')
        os.makedirs(ods_to_xlsx_dir)
        unoconv.to_xlsx(ods_filepath, ods_to_xlsx_dir)
        self.assertTrue(
            os.path.exists(os.path.join(ods_to_xlsx_dir, 'test_spreadsheet.xlsx'))
        )

        xls_to_xlsx_dir = os.path.join(self.temp_dir, 'from_xls')
        os.makedirs(xls_to_xlsx_dir)
        unoconv.to_xlsx(xls_filepath, xls_to_xlsx_dir)
        self.assertTrue(
            os.path.exists(os.path.join(xls_to_xlsx_dir, 'test_spreadsheet.xlsx'))
        )

    def test_spreadsheet_to_csv_and_back_conversions(self):
        # xlsx -> csv
        xlsx_to_csv_dir = os.path.join(self.temp_dir, 'xlsx_to_csv')
        os.makedirs(xlsx_to_csv_dir)
        unoconv.to_csv(self.xlsx_filepath, xlsx_to_csv_dir)
        csv_from_xlsx = os.path.join(xlsx_to_csv_dir, 'test_spreadsheet.csv')
        self.assertTrue(os.path.exists(csv_from_xlsx))
        with open(csv_from_xlsx, encoding='utf-8') as f:
            self.assertIn('Name,Value', f.read())

        # ods -> csv
        ods_filepath = os.path.join(self.temp_dir, 'test_spreadsheet.ods')
        unoconv.csv_to_ods(self.csv_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(ods_filepath))
        ods_to_csv_dir = os.path.join(self.temp_dir, 'ods_to_csv')
        os.makedirs(ods_to_csv_dir)
        unoconv.to_csv(ods_filepath, ods_to_csv_dir)
        csv_from_ods = os.path.join(ods_to_csv_dir, 'test_spreadsheet.csv')
        self.assertTrue(os.path.exists(csv_from_ods))
        with open(csv_from_ods, encoding='utf-8') as f:
            self.assertIn('Alpha,10', f.read())

        # xls -> csv
        xls_filepath = os.path.join(self.temp_dir, 'test_spreadsheet.xls')
        unoconv.csv_to_xls(self.csv_filepath, self.temp_dir)
        self.assertTrue(os.path.exists(xls_filepath))
        xls_to_csv_dir = os.path.join(self.temp_dir, 'xls_to_csv')
        os.makedirs(xls_to_csv_dir)
        unoconv.to_csv(xls_filepath, xls_to_csv_dir)
        csv_from_xls = os.path.join(xls_to_csv_dir, 'test_spreadsheet.csv')
        self.assertTrue(os.path.exists(csv_from_xls))
        with open(csv_from_xls, encoding='utf-8') as f:
            self.assertIn('Beta,20', f.read())

        # csv -> xlsx
        unoconv.csv_to_xlsx(self.csv_filepath, self.temp_dir)
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, 'test_spreadsheet.xlsx'))
        )

        # csv with .txt extension -> ods (requires input_filter)
        txt_csv = os.path.join(self.temp_dir, 'data.txt')
        shutil.copy(self.csv_filepath, txt_csv)
        txt_out_dir = os.path.join(self.temp_dir, 'from_txt')
        os.makedirs(txt_out_dir)
        unoconv.csv_to_ods(txt_csv, txt_out_dir)
        self.assertTrue(
            os.path.exists(os.path.join(txt_out_dir, 'data.ods'))
        )

    def test_to_csv_with_custom_delimiter_and_quotechar(self):
        semicolon_dir = os.path.join(self.temp_dir, 'csv_semicolon')
        os.makedirs(semicolon_dir)
        unoconv.to_csv(
            self.xlsx_filepath, semicolon_dir, delimiter=';', quotechar="'"
        )
        out_semicolon = os.path.join(semicolon_dir, 'test_spreadsheet.csv')
        self.assertTrue(os.path.exists(out_semicolon))
        with open(out_semicolon, encoding='utf-8') as f:
            content = f.read()
        self.assertIn("'Name';'Value'", content)
        self.assertIn("'Alpha';10", content)

        no_quote_dir = os.path.join(self.temp_dir, 'csv_no_quote')
        os.makedirs(no_quote_dir)
        unoconv.to_csv(
            self.xlsx_filepath, no_quote_dir, delimiter='|', quotechar=''
        )
        out_no_quote = os.path.join(no_quote_dir, 'test_spreadsheet.csv')
        self.assertTrue(os.path.exists(out_no_quote))
        with open(out_no_quote, encoding='utf-8') as f:
            content = f.read()
        self.assertIn('Name|Value', content)
        self.assertIn('Alpha|10', content)

    def test_converters_registry_includes_docx_and_xlsx(self):
        registered = unoconv.converters()
        docx_mime = (
            'application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document'
        )
        xlsx_mime = (
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'
        )
        self.assertEqual(
            registered[(unoconv.ODT_MIMETYPE, docx_mime)], unoconv.to_docx
        )
        self.assertEqual(
            registered[(unoconv.DOC_MIMETYPE, docx_mime)], unoconv.to_docx
        )
        self.assertEqual(
            registered[(docx_mime, unoconv.PDF_MIMETYPE)], unoconv.to_pdf
        )
        self.assertEqual(
            registered[(docx_mime, unoconv.ODT_MIMETYPE)], unoconv.to_odt
        )
        self.assertEqual(
            registered[(docx_mime, unoconv.DOC_MIMETYPE)], unoconv.to_doc
        )
        self.assertEqual(
            registered[(unoconv.CSV_MIMETYPE, unoconv.ODS_MIMETYPE)],
            unoconv.csv_to_ods,
        )
        self.assertEqual(
            registered[(unoconv.CSV_MIMETYPE, unoconv.XLS_MIMETYPE)],
            unoconv.csv_to_xls,
        )
        self.assertEqual(
            registered[(unoconv.CSV_MIMETYPE, xlsx_mime)], unoconv.csv_to_xlsx
        )
        self.assertEqual(
            registered[(unoconv.ODS_MIMETYPE, unoconv.CSV_MIMETYPE)],
            unoconv.to_csv,
        )
        self.assertEqual(
            registered[(unoconv.XLS_MIMETYPE, unoconv.CSV_MIMETYPE)],
            unoconv.to_csv,
        )
        self.assertEqual(
            registered[(xlsx_mime, unoconv.CSV_MIMETYPE)], unoconv.to_csv
        )
        self.assertEqual(
            registered[(unoconv.ODS_MIMETYPE, xlsx_mime)], unoconv.to_xlsx
        )
        self.assertEqual(
            registered[(unoconv.XLS_MIMETYPE, xlsx_mime)], unoconv.to_xlsx
        )
        self.assertEqual(
            registered[(xlsx_mime, unoconv.PDF_MIMETYPE)], unoconv.to_pdf
        )
        self.assertEqual(
            registered[(xlsx_mime, unoconv.ODS_MIMETYPE)], unoconv.to_ods
        )
        self.assertEqual(
            registered[(xlsx_mime, unoconv.XLS_MIMETYPE)], unoconv.to_xls
        )

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

    @patch('subprocess.Popen')
    def test_unoconv_passes_input_filter(self, mock_popen):
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc
        unoconv.unoconv(
            self.temp_dir,
            'ods',
            self.csv_filepath,
            input_filter=unoconv.CSV_INPUT_FILTER,
        )
        called_cmd = mock_popen.call_args.args[0]
        self.assertIn(f'--infilter={unoconv.CSV_INPUT_FILTER}', called_cmd)

    @patch.object(unoconv, 'unoconv')
    def test_convert_raises_ioerror_when_target_missing(self, mock_unoconv):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout.read.return_value = b'out'
        mock_proc.stderr.read.return_value = b'err'
        mock_unoconv.return_value = mock_proc
        with self.assertRaises(IOError):
            unoconv.convert(self.odt_filepath, self.temp_dir, 'pdf')
