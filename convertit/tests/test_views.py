from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from convertit.views import download


class DownloadTest(TestCase):
    @override_settings(CONVERTIT_DOWNLOADS_PATH='/path')
    @patch('convertit.views.download_file')
    def test_download_using_original_request_language(self,
                                                      download_file_mock):
        fakerequest = MagicMock()
        fakerequest.headers = {
            'Accept-language': 'fr',
            'Host': 'localhost:1234'
        }

        download(fakerequest, 'http://geotrek.fr')
        download_file_mock.assert_called_with('http://geotrek.fr',
                                              '/path',
                                              headers={
                                                  'Accept-language': 'fr',
                                                  'Host': 'localhost:1234'
                                              })
