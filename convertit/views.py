import os
import urllib2
from mimetypes import (
    guess_type,
    guess_extension,
)

from pyramid.view import view_config
from pyramid.url import static_url
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound,
)
from pyramid.response import Response
from convertit.helpers import (
    download_file,
    url_to_filename,
    remove_files_older_than
)


seconds_in_hour = 3600


def remove_old_files(request):
    settings = request.registry.settings

    downloads_path = settings['convertit.downloads_path']
    converted_path = settings['convertit.converted_path']

    downloads_max_age = settings.get('convertit.downloads_max_age',
                                     seconds_in_hour)
    converted_max_age = settings.get('convertit.converted_max_age',
                                     seconds_in_hour)

    remove_files_older_than(int(downloads_max_age), downloads_path)
    remove_files_older_than(int(converted_max_age), converted_path)


def download(request, url):
    downloads_path = request.registry.settings['convertit.downloads_path']

    message = "Sorry, there was an error fetching the document. Reason: %s"
    try:
        downloaded_filepath = download_file(url, downloads_path)
        return downloaded_filepath
    except ValueError as e:
        return HTTPBadRequest(message % e.message)
    except urllib2.HTTPError as e:
        return Response(message % e.reason, status_int=e.getcode())
    except urllib2.URLError as e:
        return HTTPBadRequest(message % e.reason)


@view_config(route_name='home')
def home_view(request):
    converted_path = request.registry.settings['convertit.converted_path']
    converters = request.registry.convertit

    remove_old_files(request)

    url = request.GET.get('url')
    if url is None:
        return HTTPBadRequest('Missing parameter: url')

    guessed_mimetype = guess_type(url)[0]
    input_mimetype = request.GET.get('from', guessed_mimetype)
    if not input_mimetype:
        return HTTPBadRequest('Can not guess mimetype')

    output_mimetype = request.GET.get('to', 'application/pdf')
    if (input_mimetype, output_mimetype) not in converters:
        message = 'Unsupported transform: from %s to %s (url: %s)'
        return HTTPBadRequest(message % (input_mimetype, output_mimetype, url))

    downloaded_filepath = download(request, url)
    if isinstance(downloaded_filepath, Response):
        return downloaded_filepath

    converted_extension = guess_extension(output_mimetype) or ''
    converted_filename = url_to_filename(url)
    converted_basename = converted_filename + converted_extension
    converted_filepath = os.path.join(converted_path, converted_basename)

    try:
        convert = converters[(input_mimetype, output_mimetype)]
        convert(downloaded_filepath, converted_filepath)
    except Exception as e:
        message = "Sorry, there was an error fetching the document. Reason: %s"
        return HTTPBadRequest(message % e.message)

    return HTTPFound(static_url(converted_filepath, request),
                     content_disposition='attachement; filename=%s' %
                     converted_basename)
