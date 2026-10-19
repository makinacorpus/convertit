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
        'convertit.converters.inkscape',
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
