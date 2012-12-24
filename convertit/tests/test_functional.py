import os
import shutil
import unittest
import urllib2
from webtest import TestApp
from mock import Mock, patch

from convertit import main


class FunctionalTests(unittest.TestCase):

    def setUp(self):
        here = os.path.dirname(__file__)
        self.data_path = os.path.join(here, 'data')
        self.settings = {
            'convertit.converted_path': os.path.join(self.data_path,
                                                     'converted'),
            'convertit.downloads_path': os.path.join(self.data_path,
                                                     'downloads'),
            'convertit.converted_url': 'converted',
            'convertit.converters': """
                convertit.converters.unoconv
                convertit.converters.inkscape
            """
        }
        app = main({}, **self.settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        shutil.rmtree(self.settings['convertit.converted_path'])
        shutil.rmtree(self.settings['convertit.downloads_path'])

    def odt_data(self):
        odt_path = os.path.join(self.data_path, 'test_document.odt')
        return open(odt_path).read()

    def test_no_url(self):
        "Get homepage without any `url` param"

        resp = self.testapp.get('/', status=400)
        self.assertIn('Missing parameter', resp.body)

    def test_with_invalid_url(self):
        "Get homepage with an invalid `url` param"

        request_params = {'url': 'http://example.com/foo'}
        resp = self.testapp.get('/', params=request_params,  status=400)
        self.assertIn('Can not guess mimetype', resp.body)

    def test_with_valid_url(self):
        "Get homepage with valid `url` param"

        url = 'http://example.com/test_document.odt'
        with patch.object(urllib2, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req
            resp = self.testapp.get('/', params={'url': url}, status=302)
            mock_urlopen.assert_called_once_with(url)
            filename = os.path.basename(resp.location)
            filepath = os.path.join(self.settings['convertit.converted_path'],
                                    filename)
            self.assertTrue(os.path.exists(filepath))

    def test_with_valid_url_toword(self):
        "Get homepage with valid `url` param"

        url = 'http://example.com/test_document.odt'
        converted_path = self.settings['convertit.converted_path']
        with patch.object(urllib2, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req
            request_params = {'url': url, 'to': 'application/msword'}
            resp = self.testapp.get('/', params=request_params, status=302)
            mock_urlopen.assert_called_once_with(url)
            filename = os.path.basename(resp.location)
            filepath = os.path.join(converted_path, filename)
            self.assertTrue(os.path.exists(filepath))

    def test_invalid_url_type(self):
        "Get homepage with `url` missing a protocol identifier"
        url = 'www.example.com/test_document.odt'
        resp = self.testapp.get('/', params={'url': url}, status=400)
        self.assertIn("unknown url type", resp.body)

    def test_no_such_transform(self):
        "Get homepage with `url` that triggers a DNS resolution error"
        url = 'http://example.com/test_document.odt'
        with patch.object(urllib2, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = self.odt_data()
            mock_urlopen.return_value = mock_req

            request_params = {'url': url, 'to': 'application/pdfnocontent'}
            resp = self.testapp.get('/', params=request_params, status=400)

            self.assertIn('Unsupported transform', resp.body)

    def test_invalid_hostname(self):
        "Get homepage with `url` that triggers a DNS resolution error"
        with patch.object(urllib2, 'urlopen') as mock_urlopen:
            url = 'http://example.com/test_document.odt'
            message = "Name or service not known"
            mock_urlopen.side_effect = urllib2.URLError(message)
            resp = self.testapp.get('/', params={'url': url}, status=400)
            self.assertIn("Name or service not known", resp.body)

    def test_forbidden_url(self):
        "Get homepage with `url` that is forbidden"
        with patch.object(urllib2, 'urlopen') as mock_urlopen:
            url = 'http://example.com/test_document.odt'
            mock_urlopen.side_effect = urllib2.HTTPError(url, 403,
                                                         "Forbidden access",
                                                         [], None)
            resp = self.testapp.get('/', params={'url': url}, status=403)
            self.assertIn("Forbidden access", resp.body)
