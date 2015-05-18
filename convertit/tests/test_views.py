from mock import patch, MagicMock

from pyramid.testing import DummyRequest

from convertit.views import download
from convertit.views import get_converter_options
from convertit.tests.unittest import unittest


class DownloadTest(unittest.TestCase):
    @patch('convertit.views.download_file')
    def test_download_using_original_request_language(self, download_file_mock):
        fakerequest = MagicMock()
        fakerequest.registry.settings = {'convertit.downloads_path': '/path'}
        fakerequest.headers = {'Accept-language': 'fr', 'Host': 'localhost:1234'}

        download(fakerequest, 'http://geotrek.fr')
        download_file_mock.assert_called_with('http://geotrek.fr',
                                              '/path',
                                              headers={'Accept-language': 'fr',
                                                       'Host': 'localhost:1234'})

class GetConverterOptionsTest(unittest.TestCase):

    def test_empty_dict_when_no_options(self):
        request = DummyRequest()

        options = get_converter_options({}, request)

        self.assertEqual(options, {})

    def test_empty_has_option_when_value_provided(self):
        request = DummyRequest(params={'quality': '100'})

        options = get_converter_options({
            'quality': { 'type': int }
        }, request)

        self.assertIn('quality', options)

    def test_applies_option_type(self):
        request = DummyRequest(params={'quality': '100'})

        options = get_converter_options({
            'quality': { 'type': int }
        }, request)

        self.assertIsInstance(options['quality'], int)
