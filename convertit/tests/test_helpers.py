from datetime import datetime

from mock import patch, MagicMock

from convertit.helpers import remove_files_older_than, download_file
from convertit.tests.unittest import unittest


class RemoveFilesOlderThanTests(unittest.TestCase):
    @patch('os.remove')
    @patch('datetime.datetime')
    @patch('os.path.getmtime')
    @patch('os.listdir')
    def test_outdated_file_is_removed(self, listdir_mock, getmtime_mock, datetime_mock, remove_mock):
        listdir_mock.return_value = ['foo']
        getmtime_mock.return_value = 1336858529.0
        datetime_mock.return_value = datetime.fromtimestamp(1348418372.0)

        remove_files_older_than(60, 'fake/path')

        remove_mock.assert_called_with('fake/path/foo')

    @patch('os.remove')
    @patch('datetime.datetime')
    @patch('os.path.getmtime')
    @patch('os.listdir')
    def test_not_outdated_file_is_removed(self, listdir_mock, getmtime_mock, datetime_mock, remove_mock):
        listdir_mock.return_value = ['foo']
        getmtime_mock.return_value = 1348418372.0
        datetime_mock.return_value = datetime.fromtimestamp(1336858529.0)

        remove_files_older_than(60, 'fake/path')

        remove_mock.assert_not_called()


class DownloadUrlTest(unittest.TestCase):
    @patch('urllib2.urlopen')
    def test_download_can_specify_headers(self, urlopen_mock):
        response = MagicMock()
        response.read.return_value = ''
        urlopen_mock.return_value = response

        headers = {'Accept-Language': 'fr'}
        download_file('http://geotrek.fr', '/tmp', headers=headers)
        request = urlopen_mock.call_args_list[0][0][0]
        self.assertEqual(request.headers, {'Accept-language': 'fr'})

    @patch('urllib2.urlopen')
    def test_download_headers_are_filtered(self, urlopen_mock):
        response = MagicMock()
        response.read.return_value = ''
        urlopen_mock.return_value = response

        headers = {'Accept-LANGUAGE': 'fr', 'HOST': '127.0.0.1:8001',
                   'user-agent': 'curl'}
        download_file('http://geotrek.fr', '/tmp', headers=headers)
        request = urlopen_mock.call_args_list[0][0][0]
        self.assertEqual(request.headers, {'Accept-language': 'fr',
                                           'User-agent': 'curl'})
