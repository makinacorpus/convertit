import os
import subprocess

from pyramid.config import Configurator


class MimetypeRegistry(dict):
    @property
    def ext_registry(self):
        r = {}
        for k in self:
            r[self[k]['extension']] = (k, self[k])
        return r

    def get_transform(self, *args, **kw):
        """Get a transform
        Eg::

           >>> MT.get_transform(('image/svg', 'application/pdf))
           {'method': <function to_pdf at ...>, 'extension': 'pdf'}

        """
        return self[args]


PROGRAMS = {}
CONVERTERS = MimetypeRegistry()


class TransformError(Exception):
    """Transform Error"""


def which(program):
    """Cached call to which"""
    if not program in PROGRAMS:
        PROGRAMS[program] = subprocess.check_output(['which', program]).strip()
    return PROGRAMS[program]


def exists(program=None):
    try:
        which(program)  # raise on failure
        result = True
    except:
        result = False
    return result


def create_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def test_program(program):
    def _test_program(transform_tuple, transform_callable, converters):
        return exists(program)
    return _test_program


def register(transform_tuple,
             transformed_filename_ext,
             transform_callable,
             transform_condition=None,
             converters=None):
    if converters is None:
        converters = CONVERTERS
    test = True
    if transform_condition is not None:
        if isinstance(transform_condition, bool):
            test = transform_condition
        else:
            test = transform_condition(transform_tuple, transform_callable, converters)
    if test:
        converters[transform_tuple] = {'method': transform_callable,
                                       'extension': transformed_filename_ext}


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    create_dir(settings['converted_dir'])
    create_dir(settings['download_dir'])
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view(settings['converted_url'], settings['converted_dir'],
        cache_max_age=3600)
    config.add_route('home', '/')
    config.scan(ignore='convertit.tests')
    return config.make_wsgi_app()
