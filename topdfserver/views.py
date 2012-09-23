import os
import urllib2
from mimetypes import guess_type

from pyramid.view import view_config
from pyramid.url import static_url
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPInternalServerError
from pyramid.response import Response
from .converters import unoconv, inkscape
from .helpers import download_file, url_to_filename, remove_files_older_than

converters = {}

unoconv.register(converters)
inkscape.register(converters)

seconds_in_hour = 3600


def remove_old_files(request):
    settings = request.registry.settings

    download_dir = settings['download_dir']
    converted_dir = settings['converted_dir']

    download_max_age = settings.get('download_max_age', seconds_in_hour)
    converted_max_age = settings.get('converted_max_age', seconds_in_hour)

    remove_files_older_than(int(download_max_age), download_dir)
    remove_files_older_than(int(converted_max_age), converted_dir)


@view_config(route_name='home')
def home_view(request):
    converted_dir = request.registry.settings['converted_dir']
    download_dir = request.registry.settings['download_dir']

    remove_old_files(request)

    url = request.GET.get('url')

    if url is None:
        return HTTPBadRequest('Missing parameter: url')

    mimetype, _ = guess_type(url)
    if not mimetype:
        return HTTPBadRequest('Can not guess mimetype')

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
