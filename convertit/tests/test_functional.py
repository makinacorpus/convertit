import os
import shutil
import urllib
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from convertit import create_dir

here = os.path.dirname(__file__)
data_path = os.path.join(here, 'data')
TEST_SETTINGS = {
    'CONVERTIT_CONVERTED_PATH': os.path.join(data_path, 'converted'),
    'CONVERTIT_DOWNLOADS_PATH': os.path.join(data_path, 'downloads'),
    'CONVERTIT_CONVERTED_URL': 'converted',
    'CONVERTIT_CONVERTERS': [
        'convertit.converters.unoconv',
        'convertit.converters.cairosvg',
    ],
    'CONVERTIT_CONVERTED_NAME': '{url_hostname}_{url_port}_{url_dirname}_'
                                '{url_filename}{extension}',
}


@override_settings(**TEST_SETTINGS)
class FunctionalTests(TestCase):
    def setUp(self):
        create_dir(TEST_SETTINGS['CONVERTIT_CONVERTED_PATH'])
        create_dir(TEST_SETTINGS['CONVERTIT_DOWNLOADS_PATH'])

    def tearDown(self):
        shutil.rmtree(TEST_SETTINGS['CONVERTIT_CONVERTED_PATH'])
        shutil.rmtree(TEST_SETTINGS['CONVERTIT_DOWNLOADS_PATH'])

    def odt_data(self):
        odt_path = os.path.join(data_path, 'test_document.odt')
        with open(odt_path, 'rb') as f:
            return f.read()

    def docx_data(self):
        docx_path = os.path.join(data_path, 'test_document.docx')
        with open(docx_path, 'rb') as f:
            return f.read()

    def xlsx_data(self):
        xlsx_path = os.path.join(data_path, 'test_spreadsheet.xlsx')
        with open(xlsx_path, 'rb') as f:
            return f.read()

    def csv_data(self):
        csv_path = os.path.join(data_path, 'test_spreadsheet.csv')
        with open(csv_path, 'rb') as f:
            return f.read()

    def test_no_url(self):
        "Get homepage without any `url` param"

        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(b'Missing parameter' in resp.content)

    def test_with_valid_url(self):
        "Get homepage with valid `url` param"

        url = 'http://example.com/test_document.odt'
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req
            resp = self.client.get('/', {'url': url})
            self.assertEqual(resp.status_code, 302)
            mock_urlopen.assert_called_once_with(url)
            filename = os.path.basename(resp['Location'])
            self.assertEqual(
                resp['Content-Disposition'],
                f'attachment; filename={filename}',
            )
            filepath = os.path.join(TEST_SETTINGS['CONVERTIT_CONVERTED_PATH'],
                                    filename)
            self.assertTrue(os.path.exists(filepath))
            file_resp = self.client.get(resp['Location'])
            self.assertEqual(file_resp.status_code, 200)

    def test_with_valid_url_toword(self):
        "Get homepage with valid `url` param"

        url = 'http://example.com/test_document.odt'
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req
            request_params = {'url': url, 'to': 'application/msword'}
            resp = self.client.get('/', request_params)
            self.assertEqual(resp.status_code, 302)
            mock_urlopen.assert_called_once_with(url)
            filename = os.path.basename(resp['Location'])
            filepath = os.path.join(converted_path, filename)
            self.assertTrue(os.path.exists(filepath))

    def test_invalid_url_type(self):
        "Get homepage with `url` missing a protocol identifier"
        url = 'www.example.com/test_document.odt'
        resp = self.client.get('/', {'url': url})
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(b"unknown url type" in resp.content)

    def test_x_forwarded_for_replacement(self):
        "Get supports {X_FORWARDED_FOR} placeholder in `url`"
        url = 'http://{X_FORWARDED_FOR}/test_document.odt'
        x_forwarded_for = 'domain.tld'
        expected_url = url.replace('{X_FORWARDED_FOR}', x_forwarded_for)

        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req
            resp = self.client.get('/', {'url': url},
                                   HTTP_X_FORWARDED_FOR=x_forwarded_for)
            self.assertEqual(resp.status_code, 302)
            mock_urlopen.assert_called_once_with(expected_url)
            filename = os.path.basename(resp['Location'])
            filepath = os.path.join(TEST_SETTINGS['CONVERTIT_CONVERTED_PATH'],
                                    filename)
            self.assertTrue(os.path.exists(filepath))

    def test_no_such_transform(self):
        "Get homepage with `url` that triggers a DNS resolution error"
        url = 'http://example.com/test_document.odt'
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req

            request_params = {'url': url, 'to': 'application/pdfnocontent'}
            resp = self.client.get('/', request_params)
            self.assertEqual(resp.status_code, 400)

            self.assertIn(b'Unsupported transform', resp.content)

    def test_invalid_hostname(self):
        "Get homepage with `url` that triggers a DNS resolution error"
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            url = 'http://example.com/test_document.odt'
            message = "Name or service not known"
            mock_urlopen.side_effect = urllib.error.URLError(message)
            resp = self.client.get('/', {'url': url})
            self.assertEqual(resp.status_code, 400)
            self.assertIn(b"Name or service not known", resp.content)

    def test_forbidden_url(self):
        "Get homepage with `url` that is forbidden"
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            url = 'http://example.com/test_document.odt'
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url, 403, "Forbidden access", [], None
            )
            resp = self.client.get('/', {'url': url})
            self.assertEqual(resp.status_code, 403)
            self.assertIn(b"Forbidden access", resp.content)

    def test_post(self):
        "Get post document"
        uploaded_file = SimpleUploadedFile('test_document.odt', self.odt_data())
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        resp = self.client.post('/', {'file': uploaded_file})
        self.assertEqual(resp.status_code, 302)
        filename = os.path.basename(resp['Location'])
        filepath = os.path.join(converted_path, filename)
        self.assertTrue(os.path.exists(filepath))

    def test_with_valid_url_odt_to_docx(self):
        "Convert odt document from URL to docx"
        url = 'http://example.com/test_document.odt'
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        docx_mime = (
            'application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document'
        )
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req
            resp = self.client.get('/', {'url': url, 'to': docx_mime})
            self.assertEqual(resp.status_code, 302)
            filename = os.path.basename(resp['Location'])
            self.assertTrue(filename.endswith('.docx'))
            filepath = os.path.join(converted_path, filename)
            self.assertTrue(os.path.exists(filepath))

    def test_post_docx_to_pdf_and_odt(self):
        "Post docx document and convert to pdf and odt"
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        uploaded_file = SimpleUploadedFile(
            'test_document.docx', self.docx_data()
        )
        resp = self.client.post('/', {'file': uploaded_file})
        self.assertEqual(resp.status_code, 302)
        filename = os.path.basename(resp['Location'])
        self.assertEqual(filename, 'test_document.pdf')
        self.assertTrue(os.path.exists(os.path.join(converted_path, filename)))

        uploaded_file_odt = SimpleUploadedFile(
            'test_document.docx', self.docx_data()
        )
        resp_odt = self.client.post(
            '/',
            {
                'file': uploaded_file_odt,
                'to': 'application/vnd.oasis.opendocument.text',
            },
        )
        self.assertEqual(resp_odt.status_code, 302)
        filename_odt = os.path.basename(resp_odt['Location'])
        self.assertEqual(filename_odt, 'test_document.odt')
        self.assertTrue(
            os.path.exists(os.path.join(converted_path, filename_odt))
        )

    def test_post_xlsx_to_pdf_and_ods(self):
        "Post xlsx spreadsheet and convert to pdf and ods"
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        uploaded_file = SimpleUploadedFile(
            'test_spreadsheet.xlsx', self.xlsx_data()
        )
        resp = self.client.post('/', {'file': uploaded_file})
        self.assertEqual(resp.status_code, 302)
        filename = os.path.basename(resp['Location'])
        self.assertEqual(filename, 'test_spreadsheet.pdf')
        self.assertTrue(os.path.exists(os.path.join(converted_path, filename)))

        uploaded_file_ods = SimpleUploadedFile(
            'test_spreadsheet.xlsx', self.xlsx_data()
        )
        resp_ods = self.client.post(
            '/',
            {
                'file': uploaded_file_ods,
                'to': 'application/vnd.oasis.opendocument.spreadsheet',
            },
        )
        self.assertEqual(resp_ods.status_code, 302)
        filename_ods = os.path.basename(resp_ods['Location'])
        self.assertEqual(filename_ods, 'test_spreadsheet.ods')
        self.assertTrue(
            os.path.exists(os.path.join(converted_path, filename_ods))
        )

    def test_with_valid_url_xlsx_to_xls(self):
        "Convert xlsx spreadsheet from URL to xls"
        url = 'http://example.com/test_spreadsheet.xlsx'
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.xlsx_data()
            mock_urlopen.return_value = mock_req
            resp = self.client.get(
                '/', {'url': url, 'to': 'application/vnd.ms-excel'}
            )
            self.assertEqual(resp.status_code, 302)
            filename = os.path.basename(resp['Location'])
            self.assertEqual(filename, 'test_spreadsheet.xls')
            self.assertTrue(
                os.path.exists(os.path.join(converted_path, filename))
            )

    def test_post_csv_to_ods_xls_xlsx_and_back_to_csv(self):
        "Post csv to ods/xls/xlsx and convert each spreadsheet back to csv"
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        targets = [
            ('ods', 'application/vnd.oasis.opendocument.spreadsheet'),
            ('xls', 'application/vnd.ms-excel'),
            (
                'xlsx',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            ),
        ]
        for ext, mimetype in targets:
            # csv -> ods/xls/xlsx (without explicit `from`)
            uploaded_csv = SimpleUploadedFile(
                'test_spreadsheet.csv', self.csv_data()
            )
            resp = self.client.post(
                '/', {'file': uploaded_csv, 'to': mimetype}
            )
            self.assertEqual(resp.status_code, 302)
            converted_name = os.path.basename(resp['Location'])
            self.assertEqual(converted_name, f'test_spreadsheet.{ext}')
            converted_file = os.path.join(converted_path, converted_name)
            self.assertTrue(os.path.exists(converted_file))

            # ods/xls/xlsx -> csv
            with open(converted_file, 'rb') as f:
                uploaded_sheet = SimpleUploadedFile(
                    f'roundtrip.{ext}', f.read()
                )
            resp_csv = self.client.post(
                '/', {'file': uploaded_sheet, 'to': 'text/csv'}
            )
            self.assertEqual(resp_csv.status_code, 302)
            csv_name = os.path.basename(resp_csv['Location'])
            self.assertEqual(csv_name, 'roundtrip.csv')
            csv_file = os.path.join(converted_path, csv_name)
            self.assertTrue(os.path.exists(csv_file))
            with open(csv_file, encoding='utf-8') as f:
                content = f.read()
            self.assertIn('Name,Value', content)
            self.assertIn('Alpha,10', content)
            self.assertIn('Beta,20', content)

    def test_get_xlsx_to_csv_and_csv_to_xlsx(self):
        "Convert xlsx from URL to csv and csv from URL (with legacy from) to xlsx"
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.xlsx_data()
            mock_urlopen.return_value = mock_req
            resp = self.client.get(
                '/',
                {
                    'url': 'http://example.com/test_spreadsheet.xlsx',
                    'to': 'text/csv',
                },
            )
            self.assertEqual(resp.status_code, 302)
            filename = os.path.basename(resp['Location'])
            self.assertEqual(filename, 'test_spreadsheet.csv')
            self.assertTrue(
                os.path.exists(os.path.join(converted_path, filename))
            )

        xlsx_mime = (
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'
        )
        with patch.object(urllib.request, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.csv_data()
            mock_urlopen.return_value = mock_req
            resp = self.client.get(
                '/',
                {
                    'url': 'http://example.com/test_spreadsheet.csv',
                    'from': 'plain/text',
                    'to': xlsx_mime,
                },
            )
            self.assertEqual(resp.status_code, 302)
            filename = os.path.basename(resp['Location'])
            self.assertEqual(filename, 'test_spreadsheet.xlsx')
            self.assertTrue(
                os.path.exists(os.path.join(converted_path, filename))
            )

    def test_post_xlsx_to_csv_with_options(self):
        "Post xlsx to csv with custom delimiter and quotechar"
        converted_path = TEST_SETTINGS['CONVERTIT_CONVERTED_PATH']
        uploaded_file = SimpleUploadedFile(
            'test_spreadsheet.xlsx', self.xlsx_data()
        )
        resp = self.client.post(
            '/',
            {
                'file': uploaded_file,
                'to': 'text/csv',
                'csv_delimiter': ';',
                'csv_quotechar': "'",
            },
        )
        self.assertEqual(resp.status_code, 302)
        filename = os.path.basename(resp['Location'])
        self.assertEqual(filename, 'test_spreadsheet.csv')
        csv_file = os.path.join(converted_path, filename)
        self.assertTrue(os.path.exists(csv_file))
        with open(csv_file, encoding='utf-8') as f:
            content = f.read()
        self.assertIn("'Name';'Value'", content)
        self.assertIn("'Alpha';10", content)

        # Invalid csv_delimiter returns 400
        uploaded_invalid = SimpleUploadedFile(
            'test_spreadsheet.xlsx', self.xlsx_data()
        )
        resp_invalid = self.client.post(
            '/',
            {
                'file': uploaded_invalid,
                'to': 'text/csv',
                'csv_delimiter': 'invalid',
            },
        )
        self.assertEqual(resp_invalid.status_code, 400)
        self.assertIn(b'Invalid parameter: csv_delimiter', resp_invalid.content)
