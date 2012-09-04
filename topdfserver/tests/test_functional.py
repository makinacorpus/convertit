import os
import shutil
import unittest
import urllib2
from webtest import TestApp
from mock import Mock, patch

from topdfserver import main

class FunctionalTests(unittest.TestCase):

    def setUp(self):
        here = os.path.dirname(__file__)
        self.data_dir = os.path.join(here, 'data')
        self.settings = {
            'converted_dir': os.path.join(self.data_dir, 'converted_dir'),
            'download_dir': os.path.join(self.data_dir, 'download_dir'),
        }
        app = main({}, **self.settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        shutil.rmtree(self.settings['converted_dir'])
        shutil.rmtree(self.settings['download_dir'])

    def test_no_url(self):
        "Get homepage without any `url` param"

        resp = self.testapp.get('/', status=400)
        self.assertTrue('Missing parameter' in resp.body)

    def test_with_invalid_url(self):
        "Get homepage with an invalid `url` param"

        resp = self.testapp.get('/', params={'url': 'http://example.com/foo'},  status=400)
        self.assertTrue('Unsupported mimetype' in resp.body)

    def test_with_valid_url(self):
        "Get homepage with valid `url` param"

        url = 'http://example.com/example.odt'
        odt_data = open(os.path.join(self.data_dir, 'example.odt')).read()
        with patch.object(urllib2, 'urlopen') as mock_urlopen:
            mock_req = Mock()
            mock_req.read.return_value = odt_data
            mock_urlopen.return_value = mock_req
            resp = self.testapp.get('/', params={'url': url}, status=302)
            mock_urlopen.assert_called_once_with(url)
            filename = os.path.basename(resp.location)
            filepath = os.path.join(self.settings['converted_dir'], filename)
            self.assertTrue(os.path.exists(filepath))
