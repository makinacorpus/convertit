import os
import shutil
import unittest
from webtest import TestApp

from topdfserver import main

class FunctionalTests(unittest.TestCase):

    def setUp(self):
        here = os.path.dirname(__file__)
        data_dir = os.path.join(here, 'data')
        self.settings = {
                'converted_dir': os.path.join(data_dir, 'converted_dir'),
                'download_dir': os.path.join(data_dir, 'download_dir'),
                }
        app = main({}, **self.settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        shutil.rmtree(self.settings['converted_dir'])
        shutil.rmtree(self.settings['download_dir'])


    def test_no_url(self):
        "Get homepage without any URL param"
        res = self.testapp.get('/', status=400)
