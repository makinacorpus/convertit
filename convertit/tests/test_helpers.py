from datetime import datetime

from mock import patch

from convertit.helpers import remove_files_older_than
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
