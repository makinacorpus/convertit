import os
import urllib2
from mimetypes import guess_type
from uuid import uuid4

from pyramid.view import view_config
from pyramid.url import static_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from . import odt_to_pdf, svg_to_pdf

converters = {}

odt_to_pdf.register(converters)
svg_to_pdf.register(converters)


@view_config(route_name='home')
def home_view(request):
    url = request.GET.get('url')

    if url is None:
        return HTTPBadRequest('Missing parameter: url')

    mimetype = guess_type(url)[0]

    if mimetype not in converters:
        return HTTPBadRequest('Unsupported mimetype %s' % mimetype)

    target_dir = request.registry.settings['download_dir']
    filepath = download_file(url, target_dir)

    converted_dir = request.registry.settings['converted_dir']
    converted_filepath = converters[mimetype](filepath, converted_dir)

    return HTTPFound(static_url(converted_filepath, request))


def download_file(url, target_dir):
    _, ext = os.path.splitext(url)
    data = urllib2.urlopen(url).read()
    filename = "%s%s" % (uuid4(), ext)
    target_file = os.path.join(target_dir, filename)
    with open(target_file, 'w') as f:
        f.write(data)
    return target_file
