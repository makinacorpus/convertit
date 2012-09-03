import os
import subprocess
import urllib2
from mimetypes import guess_type
from uuid import uuid4

from pyramid.view import view_config
from pyramid.url import static_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound


def odt_to_pdf(filepath, target_dir):
    command = ['unoconv', '--outputpath', target_dir, '--format', 'pdf', filepath]
    subprocess.call(command)
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    return os.path.join(target_dir, filename + '.pdf')


converters = {
    'application/vnd.oasis.opendocument.text': odt_to_pdf
}


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
    static_dir = request.registry.settings['static_dir']
    target_dir = os.path.join(static_dir, 'converted')
    converted_filepath = converters[mimetype](filepath, target_dir)

    return HTTPFound(static_url(converted_filepath, request))


def download_file(url, target_dir):
    _, ext = os.path.splitext(url)
    data = urllib2.urlopen(url).read()
    filename = "%s%s" % (uuid4(), ext)
    target_file = os.path.join(target_dir, filename) 
    with open(target_file, 'w') as f:
        f.write(data)
    return target_file
