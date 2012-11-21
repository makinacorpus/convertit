import unittest
from mock import patch
from datetime import datetime

from ..helpers import url_to_filename
from ..helpers import remove_files_older_than


class UrlToFilenameTests(unittest.TestCase):
    url_with_basename = {
        u'http://user:pass@host.tld/path/to/file': 'host-tld-path-to-file',
        u'http://user:pass@host.tld/path/to/file.ext': 'host-tld-path-to-file'
    }
    url_without_basename = {
        u'http://user:pass@host.tld/path/to/': 'host-tld-path-to',
    }

    def test_url_with_basename(self):
        for url, expected_filename in self.url_with_basename.items():
            filename = url_to_filename(url)
            self.assertEqual(filename, expected_filename)

    def test_url_without_basename(self):
        for url, expected_filename in self.url_without_basename.items():
            filename = url_to_filename(url)
            self.assertEqual(filename, expected_filename)


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
