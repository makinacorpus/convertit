from mock import patch, MagicMock

from convertit.views import download
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
