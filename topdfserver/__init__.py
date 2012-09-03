import os

from pyramid.config import Configurator


def create_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    create_dir(settings['converted_dir'])
    create_dir(settings['download_dir'])
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('converted', settings['converted_dir'],
        cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
