import os
import urllib2
from mimetypes import guess_extension

import magic
from pyramid.httpexceptions import (
    HTTPError,
    HTTPBadRequest,
    HTTPFound,
)
from pyramid.url import static_url
from pyramid.view import view_config

from convertit.helpers import (
    download_file,
    remove_files_older_than,
    render_converted_name,
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
        raise HTTPBadRequest(message % str(e))
    except urllib2.HTTPError as e:
        raise HTTPError(message % str(e), status_int=e.getcode())
    except urllib2.URLError as e:
        raise HTTPBadRequest(message % str(e))


def get_input_mimetype(request, input_filepath):
    guessed_mimetype = magic.from_file(input_filepath, mime=True)
    input_mimetype = request.GET.get('from', guessed_mimetype)

    if not input_mimetype:
        raise HTTPBadRequest('Can not guess mimetype')

    return input_mimetype


def get_converter(request, input_mimetype, output_mimetype):
    converters = request.registry.convertit

    if (input_mimetype, output_mimetype) not in converters:
        message = 'Unsupported transform: from %s to %s'
        raise HTTPBadRequest(message % (input_mimetype, output_mimetype))

    return converters[(input_mimetype, output_mimetype)]


def output_basename_from_url(request, url, mimetype):
    settings = request.registry.settings
    name_template = settings['convertit.converted_name']
    extension = guess_extension(mimetype)
    return render_converted_name(name_template, url, extension)


@view_config(route_name='home')
def home_view(request):
    settings = request.registry.settings
    converted_path = settings['convertit.converted_path']

    remove_old_files(request)

    url = request.GET.get('url')
    if url is None:
        return HTTPBadRequest('Missing parameter: url')

    input_filepath = download(request, url)
    input_mimetype = get_input_mimetype(request, input_filepath)

    output_mimetype = request.GET.get('to', 'application/pdf')
    output_basename = output_basename_from_url(request, url, output_mimetype)
    output_filepath = os.path.join(converted_path, output_basename)

    convert = get_converter(request, input_mimetype, output_mimetype)

    try:
        convert(input_filepath, output_filepath)
    except Exception as e:
        message = "Sorry, there was an error fetching the document. Reason: %s"
        return HTTPBadRequest(message % str(e))

    return HTTPFound(static_url(output_filepath, request),
                     content_disposition='attachement; filename=%s' %
                     output_basename)
