import os
import subprocess

from pyramid.config import Configurator


PROGRAMS = {}


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


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. """
    create_dir(settings['convertit.converted_path'])
    create_dir(settings['convertit.downloads_path'])

    config = Configurator(settings=settings)

    config.registry.convertit = {}

    for namespace in settings['convertit.converters'].split():
        package = config.maybe_dotted(namespace)
        config.registry.convertit.update(package.converters())

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view(settings['convertit.converted_url'],
                           settings['convertit.converted_path'],
                           cache_max_age=3600)

    config.add_route('home', '/')

    config.scan(ignore='convertit.tests')
    return config.make_wsgi_app()
