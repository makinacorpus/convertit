import unittest

from ..helpers import url_to_filename


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
