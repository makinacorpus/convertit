import importlib
import os
import tempfile
from io import BytesIO
from unittest.mock import MagicMock, patch

from django.apps import apps
from django.test import RequestFactory, TestCase, override_settings

import convertit
from convertit import asgi, gunicorn_conf, settings, urls, wsgi
from convertit.views import (
    ConvertitHttpException,
    build_converted_url,
    download,
    get_client_addr,
    get_converters,
    get_input_mimetype,
    output_basename_from_url,
    remove_old_files,
    save,
)


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


class ViewsAndCoreUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_init_exists_and_which_and_create_dir(self):
        with patch('subprocess.check_output', side_effect=Exception('not found')):
            convertit.PROGRAMS.pop('nonexistent_bin', None)
            self.assertFalse(convertit.exists('nonexistent_bin'))

        convertit.PROGRAMS['cached_bin'] = b'/usr/bin/cached_bin'
        try:
            self.assertEqual(convertit.which('cached_bin'), b'/usr/bin/cached_bin')
            self.assertTrue(convertit.exists('cached_bin'))
        finally:
            convertit.PROGRAMS.pop('cached_bin', None)

        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, 'subdir')
            convertit.create_dir(new_dir)
            self.assertTrue(os.path.exists(new_dir))
            convertit.create_dir(new_dir)
            self.assertTrue(os.path.exists(new_dir))

    def test_app_config_ready_handles_oserror(self):
        app_config = apps.get_app_config('convertit')
        with patch('convertit.apps.create_dir', side_effect=OSError('read-only')):
            app_config.ready()

    def test_wsgi_asgi_gunicorn_conf(self):
        self.assertIsNotNone(wsgi.application)
        self.assertIsNotNone(asgi.application)
        self.assertIn(':', gunicorn_conf.bind)

    def test_settings_load_ini_settings(self):
        with tempfile.NamedTemporaryFile('w', suffix='.ini', delete=False) as f:
            f.write('[app:main]\ndebug = true\n[server:main]\nport = 8000\n')
            ini_path = f.name
        try:
            with patch.dict(os.environ, {'CONVERTIT_INI': ini_path}):
                app_cfg, srv_cfg = settings.load_ini_settings()
                self.assertEqual(app_cfg['debug'], 'true')
                self.assertEqual(srv_cfg['port'], '8000')
        finally:
            os.remove(ini_path)

        with tempfile.NamedTemporaryFile('w', suffix='.ini', delete=False) as f:
            f.write('[other]\nkey = val\n')
            empty_ini_path = f.name
        try:
            with patch.dict(os.environ, {'CONVERTIT_INI': empty_ini_path}):
                app_cfg, srv_cfg = settings.load_ini_settings()
                self.assertEqual(app_cfg, {})
                self.assertEqual(srv_cfg, {})
        finally:
            os.remove(empty_ini_path)

        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists', return_value=False):
                app_cfg, srv_cfg = settings.load_ini_settings()
                self.assertEqual(app_cfg, {})
                self.assertEqual(srv_cfg, {})

    def test_urls_custom_and_external_converted_url(self):
        try:
            with override_settings(CONVERTIT_CONVERTED_URL='custom_converted'):
                importlib.reload(urls)
                names = [p.name for p in urls.urlpatterns]
                self.assertIn('converted_custom', names)

            with override_settings(CONVERTIT_CONVERTED_URL='http://example.com/converted'):
                importlib.reload(urls)
                names = [p.name for p in urls.urlpatterns]
                self.assertNotIn('converted_custom', names)

            with override_settings(CONVERTIT_CONVERTED_URL='/'):
                importlib.reload(urls)
                names = [p.name for p in urls.urlpatterns]
                self.assertNotIn('converted_custom', names)
        finally:
            importlib.reload(urls)

    def test_remove_old_files_when_paths_do_not_exist(self):
        with override_settings(
            CONVERTIT_DOWNLOADS_PATH='/nonexistent/downloads/path',
            CONVERTIT_CONVERTED_PATH='/nonexistent/converted/path',
        ):
            with patch('convertit.views.remove_files_older_than') as mock_rm:
                remove_old_files()
                mock_rm.assert_not_called()

    def test_save_without_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(CONVERTIT_DOWNLOADS_PATH=tmpdir):
                uploaded = BytesIO(b'hello')
                target = save(self.factory.post('/'), uploaded)
                self.assertTrue(os.path.exists(target))

    def test_get_input_mimetype_cannot_guess(self):
        request = self.factory.get('/')
        with patch('magic.from_file', return_value=None):
            with self.assertRaises(ConvertitHttpException) as ctx:
                get_input_mimetype(request, '/fake/file')
            self.assertEqual(ctx.exception.status, 400)
            self.assertEqual(ctx.exception.body, 'Can not guess mimetype')

    @override_settings(CONVERTIT_CONVERTERS='convertit.converters.cairosvg')
    def test_get_converters_from_string_setting(self):
        converters = get_converters()
        self.assertTrue(len(converters) > 0)

    def test_output_basename_from_url_without_dot(self):
        request = self.factory.get('/')
        name = output_basename_from_url(
            request, 'application/pdf', 'http://example.com/document'
        )
        self.assertTrue(name.endswith('.pdf'))

    def test_get_client_addr_remote_addr_fallback(self):
        request = self.factory.get('/', REMOTE_ADDR='10.0.0.1')
        self.assertEqual(get_client_addr(request), '10.0.0.1')

    def test_build_converted_url_variants(self):
        request = self.factory.get('/')
        with override_settings(CONVERTIT_CONVERTED_URL='http://cdn.example.com/files/'):
            self.assertEqual(
                build_converted_url(request, 'out.pdf'),
                'http://cdn.example.com/files/out.pdf',
            )
        with override_settings(CONVERTIT_CONVERTED_URL='/'):
            self.assertEqual(
                build_converted_url(request, 'out.pdf'),
                'http://testserver/out.pdf',
            )

    def test_home_method_not_allowed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(
                CONVERTIT_CONVERTED_PATH=os.path.join(tmpdir, 'converted'),
                CONVERTIT_DOWNLOADS_PATH=os.path.join(tmpdir, 'downloads'),
            ):
                resp = self.client.put('/')
                self.assertEqual(resp.status_code, 405)

    def test_home_post_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(
                CONVERTIT_CONVERTED_PATH=os.path.join(tmpdir, 'converted'),
                CONVERTIT_DOWNLOADS_PATH=os.path.join(tmpdir, 'downloads'),
            ):
                resp = self.client.post('/')
                self.assertEqual(resp.status_code, 400)
                self.assertIn(b'Missing parameter: file', resp.content)

    def test_home_conversion_exception_returns_500(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(
                CONVERTIT_CONVERTED_PATH=os.path.join(tmpdir, 'converted'),
                CONVERTIT_DOWNLOADS_PATH=os.path.join(tmpdir, 'downloads'),
            ):
                failing_converter = MagicMock(side_effect=RuntimeError('boom'))
                with patch('convertit.views.download', return_value='/tmp/fake.odt'):
                    with patch('convertit.views.get_input_mimetype', return_value='application/vnd.oasis.opendocument.text'):
                        with patch('convertit.views.get_converter', return_value=failing_converter):
                            resp = self.client.get('/', {'url': 'http://example.com/fake.odt'})
                            self.assertEqual(resp.status_code, 500)
                            self.assertIn(b'Sorry, there was an error converting the document. Reason: boom', resp.content)

    def test_serve_static(self):
        resp = self.client.get('/static/img/convertit_logo_light.png')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Cache-Control'], 'max-age=3600')
        resp.close()

    def test_ui_view_get_and_method_not_allowed(self):
        resp = self.client.get('/ui/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Convertir le fichier', resp.content)
        self.assertIn(b'application/pdf', resp.content)

        post_resp = self.client.post('/ui/')
        self.assertEqual(post_resp.status_code, 405)


