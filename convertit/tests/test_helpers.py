import unittest
import urllib

from freezegun import freeze_time
from mock import MagicMock, patch

from convertit.helpers import download_file, remove_files_older_than


class RemoveFilesOlderThanTests(unittest.TestCase):
    @patch('os.remove')
    @patch('os.path.getmtime')
    @patch('os.listdir')
    @freeze_time('2012-05-12 23:36:30')
    def test_outdated_file_is_removed(self, listdir_mock, getmtime_mock,
                                      remove_mock):
        listdir_mock.return_value = ['foo']
        getmtime_mock.return_value = 1336865729.0  # 2012-05-12 23:35:29

        remove_files_older_than(60, 'fake/path')

        remove_mock.assert_called_with('fake/path/foo')

    @patch('os.remove')
    @patch('os.path.getmtime')
    @patch('os.listdir')
    @freeze_time('2012-05-12 23:36:28')
    def test_not_outdated_file_is_removed(self, listdir_mock, getmtime_mock,
                                          remove_mock):
        listdir_mock.return_value = ['foo']
        getmtime_mock.return_value = 1336865729.0  # 2012-05-12 23:35:29

        remove_files_older_than(60, 'fake/path')

        remove_mock.assert_not_called()


class DownloadUrlTest(unittest.TestCase):
    @patch.object(urllib.request, 'urlopen')
    def test_download_can_specify_headers(self, urlopen_mock):
        response = MagicMock()
        response.read.return_value = b''
        urlopen_mock.return_value = response

        headers = {'Accept-Language': 'fr'}
        download_file('http://geotrek.fr', '/tmp', headers=headers)
        request = urlopen_mock.call_args_list[0][0][0]
        self.assertEqual(request.headers, {'Accept-language': 'fr'})

    @patch.object(urllib.request, 'urlopen')
    def test_download_headers_are_filtered(self, urlopen_mock):
        response = MagicMock()
        response.read.return_value = b''
        urlopen_mock.return_value = response

        headers = {'Accept-LANGUAGE': 'fr', 'HOST': '127.0.0.1:8001',
                   'user-agent': 'curl'}
        download_file('http://geotrek.fr', '/tmp', headers=headers)
        request = urlopen_mock.call_args_list[0][0][0]
        self.assertEqual(request.headers, {'Accept-language': 'fr',
                                           'User-agent': 'curl'})
