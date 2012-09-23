import os
import urllib2
from mimetypes import guess_type

from pyramid.view import view_config
from pyramid.url import static_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPInternalServerError
from pyramid.response import Response
from . import unoconv, inkscape
from .helpers import download_file, url_to_filename

converters = {}

unoconv.register(converters)
inkscape.register(converters)


@view_config(route_name='home')
def home_view(request):
    converted_dir = request.registry.settings['converted_dir']
    download_dir = request.registry.settings['download_dir']
    url = request.GET.get('url')

    if url is None:
        return HTTPBadRequest('Missing parameter: url')

    mimetype, _ = guess_type(url)
    if not mimetype:
        return HTTPInternalServerError('Can not guess mimetype')

    if mimetype in converters:
        to_pdf = converters[mimetype]
    else:
        return HTTPBadRequest('Unsupported mimetype %s' % mimetype)

    base_error_msg = "Sorry, there was an error fetching the document."
    try:
        downloaded_filepath = download_file(url, download_dir)
    except ValueError, e:
        return HTTPBadRequest(base_error_msg + " Reason: %s" % e.message)
    except urllib2.HTTPError, e:
        return Response(base_error_msg + " Reason: %s" % e.reason,
            status_int=e.getcode())
    except urllib2.URLError, e:
        return HTTPBadRequest(base_error_msg + " Reason: %s" % e.reason)

    downloaded_basename = os.path.basename(downloaded_filepath)
    downloaded_filename, _ = os.path.splitext(downloaded_basename)

    converted_filename = url_to_filename(url)
    converted_basename = converted_filename + '.pdf'
    converted_filepath = os.path.join(converted_dir, converted_basename)

    to_pdf(downloaded_filepath, converted_filepath)

    return HTTPFound(static_url(converted_filepath, request),
        content_disposition='attachement; filename=%s' % converted_basename)
